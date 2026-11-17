// Copyright 2026 Daniela Petruzalek
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"bytes"
	"compress/zlib"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/gif"
	"image/png"
	"io"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
)

const (
	aseHeaderMagic  uint16 = 0xA5E0
	aseFrameMagic   uint16 = 0xF1FA
	aseChunkLayer   uint16 = 0x2004
	aseChunkCel     uint16 = 0x2005
	aseChunkTags    uint16 = 0x2018
	aseChunkPalette uint16 = 0x2019
)

// AsepriteHeaderInfo holds parsed binary metadata from an .aseprite file for verification.
type AsepriteHeaderInfo struct {
	FileSize       uint32
	Magic          uint16
	FrameCount     uint16
	Width          uint16
	Height         uint16
	ColorDepth     uint16
	PaletteEntries uint16
	GridWidth      uint16
	GridHeight     uint16
	TagNames       []string
	CelCount       int
}

// ExportAseprite writes a CompiledSprite to a binary .aseprite file with palette, layer,
// animation tags, and ZLIB-compressed 32-bit RGBA cels.
func ExportAseprite(path string, cs *CompiledSprite) error {
	if cs == nil || len(cs.Frames) == 0 {
		return fmt.Errorf("export aseprite: compiled sprite has no frames")
	}
	if cs.FrameW <= 0 || cs.FrameH <= 0 {
		return fmt.Errorf("export aseprite: invalid frame dimensions %dx%d", cs.FrameW, cs.FrameH)
	}

	var framesBuf bytes.Buffer
	for fIdx, fr := range cs.Frames {
		var chunks [][]byte
		if fIdx == 0 {
			palChunk := buildAsePaletteChunk(cs.PaletteColors)
			layerChunk := buildAseLayerChunk("Sprite")
			chunks = append(chunks, palChunk, layerChunk)
			if len(cs.Tags) > 0 {
				tagsChunk := buildAseTagsChunk(cs.Tags)
				chunks = append(chunks, tagsChunk)
			}
		}
		celChunk, err := buildAseCelChunk(fr, cs.FrameW, cs.FrameH)
		if err != nil {
			return fmt.Errorf("export aseprite frame %d cel: %w", fIdx, err)
		}
		chunks = append(chunks, celChunk)

		dur := uint16(100)
		if fIdx < len(cs.FrameDurations) && cs.FrameDurations[fIdx] > 0 {
			dur = uint16(cs.FrameDurations[fIdx])
		}

		frameBytesSize := uint32(16)
		for _, ch := range chunks {
			frameBytesSize += uint32(len(ch))
		}

		var fHdr [16]byte
		binary.LittleEndian.PutUint32(fHdr[0:4], frameBytesSize)
		binary.LittleEndian.PutUint16(fHdr[4:6], aseFrameMagic)
		binary.LittleEndian.PutUint16(fHdr[6:8], uint16(len(chunks)))
		binary.LittleEndian.PutUint16(fHdr[8:10], dur)
		// fHdr[10:12] reserved zero
		binary.LittleEndian.PutUint32(fHdr[12:16], uint32(len(chunks)))

		framesBuf.Write(fHdr[:])
		for _, ch := range chunks {
			framesBuf.Write(ch)
		}
	}

	totalSize := uint32(128 + framesBuf.Len())
	var hdr [128]byte
	binary.LittleEndian.PutUint32(hdr[0:4], totalSize)
	binary.LittleEndian.PutUint16(hdr[4:6], aseHeaderMagic)
	binary.LittleEndian.PutUint16(hdr[6:8], uint16(len(cs.Frames)))
	binary.LittleEndian.PutUint16(hdr[8:10], uint16(cs.FrameW))
	binary.LittleEndian.PutUint16(hdr[10:12], uint16(cs.FrameH))
	binary.LittleEndian.PutUint16(hdr[12:14], 32) // 32 bpp RGBA
	binary.LittleEndian.PutUint32(hdr[14:18], 1)  // Flags: layer opacity valid
	firstDur := uint16(100)
	if len(cs.FrameDurations) > 0 && cs.FrameDurations[0] > 0 {
		firstDur = uint16(cs.FrameDurations[0])
	}
	binary.LittleEndian.PutUint16(hdr[18:20], firstDur)
	hdr[28] = 0 // transparent palette index
	numColors := len(cs.PaletteColors)
	if numColors == 0 {
		numColors = 1
	}
	if numColors > 256 {
		numColors = 256
	}
	binary.LittleEndian.PutUint16(hdr[32:34], uint16(numColors))
	hdr[34] = 1 // pixel width
	hdr[35] = 1 // pixel height
	binary.LittleEndian.PutUint16(hdr[40:42], uint16(cs.FrameW))
	binary.LittleEndian.PutUint16(hdr[42:44], uint16(cs.FrameH))

	if dir := filepath.Dir(path); dir != "" && dir != "." {
		if err := os.MkdirAll(dir, 0o755); err != nil {
			return fmt.Errorf("create output directory %q: %w", dir, err)
		}
	}

	var out bytes.Buffer
	out.Grow(int(totalSize))
	out.Write(hdr[:])
	out.Write(framesBuf.Bytes())

	if err := os.WriteFile(path, out.Bytes(), 0o644); err != nil {
		return fmt.Errorf("write aseprite file %q: %w", path, err)
	}
	return nil
}

func wrapAseChunk(chunkType uint16, payload []byte) []byte {
	total := uint32(6 + len(payload))
	buf := make([]byte, total)
	binary.LittleEndian.PutUint32(buf[0:4], total)
	binary.LittleEndian.PutUint16(buf[4:6], chunkType)
	copy(buf[6:], payload)
	return buf
}

func writeAseString(buf *bytes.Buffer, s string) {
	b := []byte(s)
	var lenBytes [2]byte
	binary.LittleEndian.PutUint16(lenBytes[:], uint16(len(b)))
	buf.Write(lenBytes[:])
	buf.Write(b)
}

func buildAsePaletteChunk(colors []color.RGBA) []byte {
	if len(colors) == 0 {
		colors = []color.RGBA{{0, 0, 0, 0}}
	}
	if len(colors) > 256 {
		colors = colors[:256]
	}
	var payload bytes.Buffer
	var head [20]byte
	binary.LittleEndian.PutUint32(head[0:4], uint32(len(colors)))
	binary.LittleEndian.PutUint32(head[4:8], 0)
	binary.LittleEndian.PutUint32(head[8:12], uint32(len(colors)-1))
	payload.Write(head[:])
	for _, c := range colors {
		var entry [6]byte
		// entry[0:2] flags = 0
		entry[2] = c.R
		entry[3] = c.G
		entry[4] = c.B
		entry[5] = c.A
		payload.Write(entry[:])
	}
	return wrapAseChunk(aseChunkPalette, payload.Bytes())
}

func buildAseLayerChunk(name string) []byte {
	var payload bytes.Buffer
	var fixed [16]byte
	binary.LittleEndian.PutUint16(fixed[0:2], 3) // Visible (1) | Editable (2)
	binary.LittleEndian.PutUint16(fixed[2:4], 0) // Normal image layer
	binary.LittleEndian.PutUint16(fixed[4:6], 0) // Child level 0
	binary.LittleEndian.PutUint16(fixed[10:12], 0) // Blend mode normal
	fixed[12] = 255                                // Opacity 255
	payload.Write(fixed[:])
	writeAseString(&payload, name)
	return wrapAseChunk(aseChunkLayer, payload.Bytes())
}

func buildAseTagsChunk(tags []CompiledTag) []byte {
	var payload bytes.Buffer
	var head [10]byte
	binary.LittleEndian.PutUint16(head[0:2], uint16(len(tags)))
	payload.Write(head[:])
	for _, t := range tags {
		var entry [17]byte
		binary.LittleEndian.PutUint16(entry[0:2], uint16(t.FromFrame))
		binary.LittleEndian.PutUint16(entry[2:4], uint16(t.ToFrame))
		var loopDir byte
		var repeat uint16
		switch t.Loop {
		case "reverse":
			loopDir = 1
		case "pingpong":
			loopDir = 2
		case "once":
			loopDir = 0
			repeat = 1
		default:
			loopDir = 0
		}
		entry[4] = loopDir
		binary.LittleEndian.PutUint16(entry[5:7], repeat)
		if t.LoopFromFrame > t.FromFrame && t.LoopFromFrame <= t.ToFrame {
			binary.LittleEndian.PutUint16(entry[7:9], uint16(t.LoopFromFrame))
			entry[9] = 1
		}
		// Tag color RGB in bytes 13..15
		entry[13] = 0x42
		entry[14] = 0xB6
		entry[15] = 0xF5
		payload.Write(entry[:])
		writeAseString(&payload, t.Name)
	}
	return wrapAseChunk(aseChunkTags, payload.Bytes())
}

func buildAseCelChunk(fr *image.RGBA, w, h int) ([]byte, error) {
	rawRGBA := make([]byte, w*h*4)
	idx := 0
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			c := fr.RGBAAt(x, y)
			rawRGBA[idx] = c.R
			rawRGBA[idx+1] = c.G
			rawRGBA[idx+2] = c.B
			rawRGBA[idx+3] = c.A
			idx += 4
		}
	}

	var zbuf bytes.Buffer
	zw := zlib.NewWriter(&zbuf)
	if _, err := zw.Write(rawRGBA); err != nil {
		_ = zw.Close()
		return nil, err
	}
	if err := zw.Close(); err != nil {
		return nil, err
	}

	var payload bytes.Buffer
	var fixed [20]byte
	binary.LittleEndian.PutUint16(fixed[0:2], 0) // Layer index 0
	binary.LittleEndian.PutUint16(fixed[2:4], 0) // X = 0
	binary.LittleEndian.PutUint16(fixed[4:6], 0) // Y = 0
	fixed[6] = 255                               // Opacity = 255
	binary.LittleEndian.PutUint16(fixed[7:9], 2) // Cel type 2 = Compressed Image
	// fixed[9:16] Z-index and reserved zeros
	binary.LittleEndian.PutUint16(fixed[16:18], uint16(w))
	binary.LittleEndian.PutUint16(fixed[18:20], uint16(h))
	payload.Write(fixed[:])
	payload.Write(zbuf.Bytes())

	return wrapAseChunk(aseChunkCel, payload.Bytes()), nil
}

// ReadAsepriteHeader reads and validates the binary structure, frame headers, tags, and cels of an .aseprite file.
func ReadAsepriteHeader(path string) (*AsepriteHeaderInfo, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read aseprite file %q: %w", path, err)
	}
	if len(data) < 128 {
		return nil, fmt.Errorf("file %q is too small (%d bytes) for 128-byte ASE header", path, len(data))
	}
	info := &AsepriteHeaderInfo{
		FileSize:       binary.LittleEndian.Uint32(data[0:4]),
		Magic:          binary.LittleEndian.Uint16(data[4:6]),
		FrameCount:     binary.LittleEndian.Uint16(data[6:8]),
		Width:          binary.LittleEndian.Uint16(data[8:10]),
		Height:         binary.LittleEndian.Uint16(data[10:12]),
		ColorDepth:     binary.LittleEndian.Uint16(data[12:14]),
		PaletteEntries: binary.LittleEndian.Uint16(data[32:34]),
		GridWidth:      binary.LittleEndian.Uint16(data[40:42]),
		GridHeight:     binary.LittleEndian.Uint16(data[42:44]),
	}
	if info.Magic != aseHeaderMagic {
		return nil, fmt.Errorf("invalid ASE header magic 0x%04X (expected 0xA5E0)", info.Magic)
	}
	if int(info.FileSize) != len(data) {
		return nil, fmt.Errorf("header file size %d does not match actual byte length %d", info.FileSize, len(data))
	}

	offset := 128
	for f := 0; f < int(info.FrameCount); f++ {
		if offset+16 > len(data) {
			return nil, fmt.Errorf("truncated frame %d header at offset %d", f, offset)
		}
		fSize := int(binary.LittleEndian.Uint32(data[offset : offset+4]))
		fMagic := binary.LittleEndian.Uint16(data[offset+4 : offset+6])
		if fMagic != aseFrameMagic {
			return nil, fmt.Errorf("frame %d has invalid magic 0x%04X (expected 0xF1FA)", f, fMagic)
		}
		numChunks := int(binary.LittleEndian.Uint32(data[offset+12 : offset+16]))
		if numChunks == 0 {
			numChunks = int(binary.LittleEndian.Uint16(data[offset+6 : offset+8]))
		}
		cOff := offset + 16
		for c := 0; c < numChunks; c++ {
			if cOff+6 > offset+fSize || cOff+6 > len(data) {
				return nil, fmt.Errorf("frame %d chunk %d header out of bounds", f, c)
			}
			cSize := int(binary.LittleEndian.Uint32(data[cOff : cOff+4]))
			cType := binary.LittleEndian.Uint16(data[cOff+4 : cOff+6])
			if cSize < 6 || cOff+cSize > len(data) {
				return nil, fmt.Errorf("frame %d chunk %d invalid size %d", f, c, cSize)
			}
			payload := data[cOff+6 : cOff+cSize]
			if cType == aseChunkTags && len(payload) >= 10 {
				tCount := int(binary.LittleEndian.Uint16(payload[0:2]))
				pOff := 10
				for ti := 0; ti < tCount && pOff+19 <= len(payload); ti++ {
					sLen := int(binary.LittleEndian.Uint16(payload[pOff+17 : pOff+19]))
					pOff += 19
					if pOff+sLen <= len(payload) {
						info.TagNames = append(info.TagNames, string(payload[pOff:pOff+sLen]))
						pOff += sLen
					}
				}
			} else if cType == aseChunkCel {
				info.CelCount++
			}
			cOff += cSize
		}
		offset += fSize
	}
	return info, nil
}

// ImportAseprite decodes a binary .aseprite file into a CompiledSprite, extracting all frames,
// frame durations, ZLIB-compressed RGBA cels, and animation tags.
func ImportAseprite(path string) (*CompiledSprite, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read aseprite file %q: %w", path, err)
	}
	if len(data) < 128 {
		return nil, fmt.Errorf("file %q is too small (%d bytes) for 128-byte ASE header", path, len(data))
	}
	magic := binary.LittleEndian.Uint16(data[4:6])
	if magic != aseHeaderMagic {
		return nil, fmt.Errorf("invalid ASE header magic 0x%04X (expected 0xA5E0)", magic)
	}
	frameCount := int(binary.LittleEndian.Uint16(data[6:8]))
	fw := int(binary.LittleEndian.Uint16(data[8:10]))
	fh := int(binary.LittleEndian.Uint16(data[10:12]))
	if frameCount <= 0 || fw <= 0 || fh <= 0 {
		return nil, fmt.Errorf("invalid ASE dimensions: %d frames, %dx%d", frameCount, fw, fh)
	}

	frames := make([]*image.RGBA, frameCount)
	durations := make([]int, frameCount)
	for i := 0; i < frameCount; i++ {
		frames[i] = image.NewRGBA(image.Rect(0, 0, fw, fh))
		durations[i] = 100
	}

	type rawTag struct {
		name          string
		fromFrame     int
		loopFromFrame int
		toFrame       int
		loop          string
	}
	var rawTags []rawTag

	offset := 128
	for f := 0; f < frameCount && offset+16 <= len(data); f++ {
		fSize := int(binary.LittleEndian.Uint32(data[offset : offset+4]))
		fMagic := binary.LittleEndian.Uint16(data[offset+4 : offset+6])
		if fMagic != aseFrameMagic {
			return nil, fmt.Errorf("frame %d has invalid magic 0x%04X", f, fMagic)
		}
		fDur := int(binary.LittleEndian.Uint16(data[offset+8 : offset+10]))
		if fDur > 0 {
			durations[f] = fDur
		}
		numChunks := int(binary.LittleEndian.Uint32(data[offset+12 : offset+16]))
		if numChunks == 0 {
			numChunks = int(binary.LittleEndian.Uint16(data[offset+6 : offset+8]))
		}
		cOff := offset + 16
		for c := 0; c < numChunks && cOff+6 <= offset+fSize && cOff+6 <= len(data); c++ {
			cSize := int(binary.LittleEndian.Uint32(data[cOff : cOff+4]))
			cType := binary.LittleEndian.Uint16(data[cOff+4 : cOff+6])
			if cSize < 6 || cOff+cSize > len(data) {
				break
			}
			payload := data[cOff+6 : cOff+cSize]
			switch cType {
			case aseChunkTags:
				if len(payload) >= 10 {
					tCount := int(binary.LittleEndian.Uint16(payload[0:2]))
					pOff := 10
					for ti := 0; ti < tCount && pOff+19 <= len(payload); ti++ {
						fromF := int(binary.LittleEndian.Uint16(payload[pOff : pOff+2]))
						toF := int(binary.LittleEndian.Uint16(payload[pOff+2 : pOff+4]))
						loopDir := payload[pOff+4]
						repeat := binary.LittleEndian.Uint16(payload[pOff+5 : pOff+7])
						loopFromCand := int(binary.LittleEndian.Uint16(payload[pOff+7 : pOff+9]))
						hasLoopFrom := payload[pOff+9] == 1
						sLen := int(binary.LittleEndian.Uint16(payload[pOff+17 : pOff+19]))
						pOff += 19
						if pOff+sLen <= len(payload) {
							tName := string(payload[pOff : pOff+sLen])
							pOff += sLen
							loopStr := "loop"
							if loopDir == 1 {
								loopStr = "reverse"
							} else if loopDir == 2 {
								loopStr = "pingpong"
							} else if repeat == 1 {
								loopStr = "once"
							}
							var loopFromF int
							if hasLoopFrom && loopFromCand > fromF && loopFromCand <= toF {
								loopFromF = loopFromCand
							}
							rawTags = append(rawTags, rawTag{
								name:          tName,
								fromFrame:     fromF,
								loopFromFrame: loopFromF,
								toFrame:       toF,
								loop:          loopStr,
							})
						}
					}
				}
			case aseChunkCel:
				if len(payload) >= 20 {
					celX := int(int16(binary.LittleEndian.Uint16(payload[2:4])))
					celY := int(int16(binary.LittleEndian.Uint16(payload[4:6])))
					celType := binary.LittleEndian.Uint16(payload[7:9])
					celW := int(binary.LittleEndian.Uint16(payload[16:18]))
					celH := int(binary.LittleEndian.Uint16(payload[18:20]))
					if celType == 2 && celW > 0 && celH > 0 {
						zr, zErr := zlib.NewReader(bytes.NewReader(payload[20:]))
						if zErr == nil {
							rawBytes := make([]byte, celW*celH*4)
							_, _ = io.ReadFull(zr, rawBytes)
							_ = zr.Close()
							dst := frames[f]
							idx := 0
							for y := 0; y < celH; y++ {
								for x := 0; x < celW; x++ {
									cCol := PremultiplyRGBA(rawBytes[idx], rawBytes[idx+1], rawBytes[idx+2], rawBytes[idx+3])
									idx += 4
									if cCol.A > 0 {
										dx, dy := celX+x, celY+y
										if dx >= 0 && dx < fw && dy >= 0 && dy < fh {
											dst.SetRGBA(dx, dy, cCol)
										}
									}
								}
							}
						}
					}
				}
			}
			cOff += cSize
		}
		offset += fSize
	}

	var tags []CompiledTag
	for _, rt := range rawTags {
		dur := 100
		if rt.fromFrame >= 0 && rt.fromFrame < len(durations) && durations[rt.fromFrame] > 0 {
			dur = durations[rt.fromFrame]
		}
		tags = append(tags, CompiledTag{
			Name:          rt.name,
			FromFrame:     rt.fromFrame,
			LoopFromFrame: rt.loopFromFrame,
			ToFrame:       rt.toFrame,
			Frames:        rt.toFrame - rt.fromFrame + 1,
			DurationMs:    dur,
			Loop:          rt.loop,
		})
	}
	if len(tags) == 0 {
		tags = []CompiledTag{
			{
				Name:       "idle",
				FromFrame:  0,
				ToFrame:    frameCount - 1,
				Frames:     frameCount,
				DurationMs: durations[0],
				Loop:       "loop",
			},
		}
	}

	cols := 4
	if frameCount < 4 {
		cols = frameCount
	} else if frameCount > 16 && len(tags) > 0 && tags[0].Frames > 0 {
		cols = tags[0].Frames
	}
	rows := (frameCount + cols - 1) / cols
	sheetRGBA := image.NewRGBA(image.Rect(0, 0, cols*fw, rows*fh))
	for i, fr := range frames {
		c := i % cols
		r := i / cols
		dstRect := image.Rect(c*fw, r*fh, (c+1)*fw, (r+1)*fh)
		draw.Draw(sheetRGBA, dstRect, fr, image.Point{0, 0}, draw.Src)
	}

	stem := strings.TrimSuffix(filepath.Base(path), filepath.Ext(path))
	return &CompiledSprite{
		Title:          stem,
		Type:           "sprite",
		FrameW:         fw,
		FrameH:         fh,
		Palette:        "custom",
		Frames:         frames,
		FrameDurations: durations,
		Tags:           tags,
		Parts:          []PartSummary{},
		PaletteColors:  collectUniqueColors(sheetRGBA),
		SheetRGBA:      sheetRGBA,
		SheetCols:      cols,
		SheetRows:      rows,
	}, nil
}

// ExportSpriteContainer writes a declarative .sprite container file referencing the packed PNG sheet
// alongside its frame dimensions, grid layout, and animation tags.
func ExportSpriteContainer(spritePath, pngFileName string, cs *CompiledSprite) error {
	if cs == nil {
		return fmt.Errorf("export sprite container: compiled sprite is nil")
	}
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("title %q\n", cs.Title))
	sb.WriteString(fmt.Sprintf("type %s\n", cs.Type))
	sb.WriteString(fmt.Sprintf("sheet %q\n", filepath.Base(pngFileName)))
	sb.WriteString(fmt.Sprintf("size %dx%d\n", cs.FrameW, cs.FrameH))
	sb.WriteString(fmt.Sprintf("grid %dx%d\n", cs.SheetCols, cs.SheetRows))

	uniformDur := 100
	isUniform := true
	if len(cs.Tags) > 0 && cs.Tags[0].DurationMs > 0 {
		uniformDur = cs.Tags[0].DurationMs
	}
	for _, t := range cs.Tags {
		if t.DurationMs > 0 && t.DurationMs != uniformDur {
			isUniform = false
			break
		}
	}
	if isUniform && uniformDur != 100 {
		if 1000%uniformDur == 0 {
			sb.WriteString(fmt.Sprintf("fps %d\n", 1000/uniformDur))
		} else {
			sb.WriteString(fmt.Sprintf("duration %dms\n", uniformDur))
		}
	}
	sb.WriteString("\n")

	for _, t := range cs.Tags {
		loopMode := FormatLoopMode(t.Loop)
		if t.LoopFromFrame > t.FromFrame && t.LoopFromFrame <= t.ToFrame {
			introRange := fmt.Sprintf("%d", t.FromFrame)
			if t.LoopFromFrame-1 > t.FromFrame {
				introRange = fmt.Sprintf("%d..%d", t.FromFrame, t.LoopFromFrame-1)
			}
			loopRange := fmt.Sprintf("%d", t.LoopFromFrame)
			if t.ToFrame > t.LoopFromFrame {
				loopRange = fmt.Sprintf("%d..%d", t.LoopFromFrame, t.ToFrame)
			}
			if isUniform {
				sb.WriteString(fmt.Sprintf("tag %-10s %s once, %s %s\n", t.Name, introRange, loopRange, loopMode))
			} else {
				sb.WriteString(fmt.Sprintf("tag %-10s %s once, %s %dms %s\n", t.Name, introRange, loopRange, t.DurationMs, loopMode))
			}
		} else {
			frameRange := fmt.Sprintf("%d..%d", t.FromFrame, t.ToFrame)
			if t.FromFrame == t.ToFrame {
				frameRange = fmt.Sprintf("%d", t.FromFrame)
			}
			if isUniform {
				sb.WriteString(fmt.Sprintf("tag %-10s %s %s\n", t.Name, frameRange, loopMode))
			} else {
				sb.WriteString(fmt.Sprintf("tag %-10s %s %dms %s\n", t.Name, frameRange, t.DurationMs, loopMode))
			}
		}
	}
	if dir := filepath.Dir(spritePath); dir != "" && dir != "." {
		if err := os.MkdirAll(dir, 0o755); err != nil {
			return err
		}
	}
	return os.WriteFile(spritePath, []byte(sb.String()), 0o644)
}

// AsepriteSheetJSON represents an Aseprite-compatible sprite sheet metadata JSON manifest.
type AsepriteSheetJSON struct {
	Frames []AsepriteFrameEntry `json:"frames"`
	Meta   AsepriteMetaJSON     `json:"meta"`
}

// AsepriteRectJSON represents a pixel rectangle in the JSON manifest.
type AsepriteRectJSON struct {
	X int `json:"x"`
	Y int `json:"y"`
	W int `json:"w"`
	H int `json:"h"`
}

// AsepriteSizeJSON represents width and height dimensions.
type AsepriteSizeJSON struct {
	W int `json:"w"`
	H int `json:"h"`
}

// AsepriteFrameEntry describes one frame's coordinates and timing in the atlas.
type AsepriteFrameEntry struct {
	Filename         string           `json:"filename"`
	Frame            AsepriteRectJSON `json:"frame"`
	Rotated          bool             `json:"rotated"`
	Trimmed          bool             `json:"trimmed"`
	SpriteSourceSize AsepriteRectJSON `json:"spriteSourceSize"`
	SourceSize       AsepriteSizeJSON `json:"sourceSize"`
	Duration         int              `json:"duration"`
}

// AsepriteMetaJSON describes the sprite sheet metadata and animation frameTags.
type AsepriteMetaJSON struct {
	App         string            `json:"app"`
	Version     string            `json:"version"`
	Image       string            `json:"image"`
	Format      string            `json:"format"`
	Size        AsepriteSizeJSON  `json:"size"`
	FrameWidth  int               `json:"frameWidth"`
	FrameHeight int               `json:"frameHeight"`
	Cols        int               `json:"cols"`
	Rows        int               `json:"rows"`
	Scale       string            `json:"scale"`
	FrameTags   []CompiledTag     `json:"frameTags"`
}

// ExportPreviewPNG writes a nearest-neighbor magnified PNG preview of the sprite sheet
// (with a subtle dark checkerboard background so dark outlines remain visible) for human visual inspection.
func ExportPreviewPNG(previewPath string, scale int, cs *CompiledSprite) error {
	if cs == nil || cs.SheetRGBA == nil {
		return fmt.Errorf("export preview PNG: compiled sprite or SheetRGBA is nil")
	}
	if scale < 1 {
		scale = 4
	}
	if scale > 16 {
		scale = 16
	}
	b := cs.SheetRGBA.Bounds()
	w, h := b.Dx(), b.Dy()
	outW, outH := w*scale, h*scale
	out := image.NewRGBA(image.Rect(0, 0, outW, outH))

	bgA := color.RGBA{R: 34, G: 32, B: 48, A: 255}
	bgB := color.RGBA{R: 44, G: 41, B: 62, A: 255}

	for y := 0; y < outH; y++ {
		srcY := y / scale
		cellRow := srcY / cs.FrameH
		for x := 0; x < outW; x++ {
			srcX := x / scale
			cellCol := srcX / cs.FrameW
			c := cs.SheetRGBA.RGBAAt(srcX, srcY)
			if c.A == 255 {
				out.SetRGBA(x, y, c)
			} else {
				// Subtle frame grid & 4px checkerboard behind transparent pixels
				bg := bgA
				if ((srcX/4)+(srcY/4))%2 == 1 {
					bg = bgB
				}
				if (srcX%cs.FrameW == 0 || srcY%cs.FrameH == 0) && (x%scale == 0 || y%scale == 0) {
					bg = color.RGBA{R: 64, G: 60, B: 88, A: 255}
				}
				_ = cellRow
				_ = cellCol
				if c.A == 0 {
					out.SetRGBA(x, y, bg)
				} else {
					invA := uint16(255 - c.A)
					out.SetRGBA(x, y, color.RGBA{
						R: c.R + uint8((uint16(bg.R)*invA+127)/255),
						G: c.G + uint8((uint16(bg.G)*invA+127)/255),
						B: c.B + uint8((uint16(bg.B)*invA+127)/255),
						A: 255,
					})
				}
			}
		}
	}

	if dir := filepath.Dir(previewPath); dir != "" && dir != "." {
		if err := os.MkdirAll(dir, 0o755); err != nil {
			return fmt.Errorf("create preview PNG directory %q: %w", dir, err)
		}
	}
	f, err := os.Create(previewPath)
	if err != nil {
		return fmt.Errorf("create preview PNG %q: %w", previewPath, err)
	}
	encErr := png.Encode(f, out)
	closeErr := f.Close()
	if encErr != nil {
		return fmt.Errorf("encode preview PNG %q: %w", previewPath, encErr)
	}
	return closeErr
}

// ExportTagGIFs writes a nearest-neighbor magnified animated .gif preview for each animation tag
// in cs.Tags into gifDir (named "<prefix>_<tag>.gif") and returns the written file paths.
func ExportTagGIFs(gifDir, prefix string, scale int, cs *CompiledSprite) ([]string, error) {
	if cs == nil || len(cs.Frames) == 0 {
		return nil, fmt.Errorf("export tag GIFs: compiled sprite has no frames")
	}
	if gifDir == "" {
		return nil, fmt.Errorf("export tag GIFs: gifDir is empty")
	}
	if scale < 1 {
		scale = 4
	}
	if scale > 16 {
		scale = 16
	}
	if err := os.MkdirAll(gifDir, 0o755); err != nil {
		return nil, fmt.Errorf("create GIF directory %q: %w", gifDir, err)
	}

	cleanPrefix := strings.TrimSpace(prefix)
	if cleanPrefix == "" {
		cleanPrefix = "sprite"
	}

	tags := cs.Tags
	if len(tags) == 0 {
		tags = []CompiledTag{
			{
				Name:       "idle",
				FromFrame:  0,
				ToFrame:    len(cs.Frames) - 1,
				Frames:     len(cs.Frames),
				DurationMs: 100,
				Loop:       "forward",
			},
		}
	}

	var written []string
	for _, tag := range tags {
		if tag.FromFrame < 0 || tag.ToFrame >= len(cs.Frames) || tag.FromFrame > tag.ToFrame {
			continue
		}
		var indices []int
		switch strings.ToLower(tag.Loop) {
		case "reverse":
			for i := tag.ToFrame; i >= tag.FromFrame; i-- {
				indices = append(indices, i)
			}
		case "pingpong":
			for i := tag.FromFrame; i <= tag.ToFrame; i++ {
				indices = append(indices, i)
			}
			for i := tag.ToFrame - 1; i > tag.FromFrame; i-- {
				indices = append(indices, i)
			}
		default:
			for i := tag.FromFrame; i <= tag.ToFrame; i++ {
				indices = append(indices, i)
			}
		}

		anim := &gif.GIF{
			LoopCount: 0, // Loop forever for preview inspection
		}
		for _, fIdx := range indices {
			palImg := renderScaledGIFFrame(cs.Frames[fIdx], cs.FrameW, cs.FrameH, scale)
			durMs := tag.DurationMs
			if fIdx < len(cs.FrameDurations) && cs.FrameDurations[fIdx] > 0 {
				durMs = cs.FrameDurations[fIdx]
			}
			if durMs <= 0 {
				durMs = 100
			}
			delayCs := (durMs + 5) / 10
			if delayCs < 2 {
				delayCs = 2
			}
			anim.Image = append(anim.Image, palImg)
			anim.Delay = append(anim.Delay, delayCs)
		}

		safeTag := strings.Map(func(r rune) rune {
			if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '_' || r == '-' {
				return r
			}
			return '_'
		}, tag.Name)
		outPath := filepath.Join(gifDir, fmt.Sprintf("%s_%s.gif", cleanPrefix, safeTag))
		f, err := os.Create(outPath)
		if err != nil {
			return written, fmt.Errorf("create GIF %q: %w", outPath, err)
		}
		encErr := gif.EncodeAll(f, anim)
		closeErr := f.Close()
		if encErr != nil {
			return written, fmt.Errorf("encode GIF %q: %w", outPath, encErr)
		}
		if closeErr != nil {
			return written, closeErr
		}
		written = append(written, outPath)
	}

	return written, nil
}

func renderScaledGIFFrame(src *image.RGBA, frameW, frameH, scale int) *image.Paletted {
	outW, outH := frameW*scale, frameH*scale
	rgba := image.NewRGBA(image.Rect(0, 0, outW, outH))

	// High-contrast neutral slate studio checkerboard + ground baseline so dark outlines are crystal clear
	bgA := color.RGBA{R: 54, G: 52, B: 72, A: 255}
	bgB := color.RGBA{R: 66, G: 64, B: 88, A: 255}
	groundLine := color.RGBA{R: 86, G: 82, B: 112, A: 255}
	groundY := frameH - 2

	for y := 0; y < outH; y++ {
		srcY := y / scale
		for x := 0; x < outW; x++ {
			srcX := x / scale
			bg := bgA
			if ((srcX/4)+(srcY/4))%2 == 1 {
				bg = bgB
			}
			if srcY == groundY && y%scale == scale-1 {
				bg = groundLine
			}
			c := src.RGBAAt(srcX, srcY)
			if c.A == 255 {
				rgba.SetRGBA(x, y, c)
			} else if c.A == 0 {
				rgba.SetRGBA(x, y, bg)
			} else {
				invA := uint16(255 - c.A)
				rgba.SetRGBA(x, y, color.RGBA{
					R: c.R + uint8((uint16(bg.R)*invA+127)/255),
					G: c.G + uint8((uint16(bg.G)*invA+127)/255),
					B: c.B + uint8((uint16(bg.B)*invA+127)/255),
					A: 255,
				})
			}
		}
	}

	// Build up to 256-color palette from the frame's colors
	type colFreq struct {
		c   color.RGBA
		cnt int
	}
	freq := make(map[color.RGBA]int)
	for y := 0; y < outH; y++ {
		for x := 0; x < outW; x++ {
			c := rgba.RGBAAt(x, y)
			// Quantize to 6-bit per channel if many colors
			qc := color.RGBA{R: c.R & 0xFC, G: c.G & 0xFC, B: c.B & 0xFC, A: 255}
			freq[qc]++
		}
	}

	list := make([]colFreq, 0, len(freq))
	for c, n := range freq {
		list = append(list, colFreq{c: c, cnt: n})
	}
	sort.Slice(list, func(i, j int) bool {
		if list[i].cnt != list[j].cnt {
			return list[i].cnt > list[j].cnt
		}
		if list[i].c.R != list[j].c.R {
			return list[i].c.R < list[j].c.R
		}
		if list[i].c.G != list[j].c.G {
			return list[i].c.G < list[j].c.G
		}
		return list[i].c.B < list[j].c.B
	})

	pal := make(color.Palette, 0, 256)
	pal = append(pal, bgA, bgB, groundLine)
	seenPal := map[color.RGBA]uint8{
		bgA:        0,
		bgB:        1,
		groundLine: 2,
	}
	// Pass 1: Add distinct colors separated by at least 24 Manhattan RGB units so small accents
	// (eyes, gold bells, collar highlights) are guaranteed palette slots before smooth gradients fill the rest.
	for _, minDist := range []int{28, 14, 0} {
		for _, item := range list {
			if len(pal) >= 256 {
				break
			}
			if _, exists := seenPal[item.c]; exists {
				continue
			}
			if minDist > 0 {
				tooClose := false
				for _, pc := range pal {
					if colorDistManhattan(item.c, pc.(color.RGBA)) < minDist {
						tooClose = true
						break
					}
				}
				if tooClose {
					continue
				}
			}
			seenPal[item.c] = uint8(len(pal))
			pal = append(pal, item.c)
		}
	}

	palImg := image.NewPaletted(image.Rect(0, 0, outW, outH), pal)
	lookupCache := make(map[color.RGBA]uint8, len(freq))
	for y := 0; y < outH; y++ {
		for x := 0; x < outW; x++ {
			c := rgba.RGBAAt(x, y)
			qc := color.RGBA{R: c.R & 0xFC, G: c.G & 0xFC, B: c.B & 0xFC, A: 255}
			if idx, ok := seenPal[c]; ok {
				palImg.SetColorIndex(x, y, idx)
				continue
			}
			if idx, ok := seenPal[qc]; ok {
				palImg.SetColorIndex(x, y, idx)
				continue
			}
			if idx, ok := lookupCache[qc]; ok {
				palImg.SetColorIndex(x, y, idx)
				continue
			}
			bestIdx := uint8(0)
			bestDist := 1 << 30
			for pi, pc := range pal {
				pr := pc.(color.RGBA)
				d := colorDistManhattan(qc, pr)
				if d < bestDist {
					bestDist = d
					bestIdx = uint8(pi)
				}
			}
			lookupCache[qc] = bestIdx
			palImg.SetColorIndex(x, y, bestIdx)
		}
	}
	return palImg
}

// ExportPNGSheet writes the packed RGBA sprite sheet to pngPath and optionally writes an
// Aseprite-compatible JSON manifest to jsonPath.
func ExportPNGSheet(pngPath, jsonPath string, cs *CompiledSprite) error {
	if cs == nil || cs.SheetRGBA == nil {
		return fmt.Errorf("export PNG sheet: compiled sprite or SheetRGBA is nil")
	}
	if pngPath != "" {
		if dir := filepath.Dir(pngPath); dir != "" && dir != "." {
			if err := os.MkdirAll(dir, 0o755); err != nil {
				return fmt.Errorf("create PNG output directory %q: %w", dir, err)
			}
		}
		f, err := os.Create(pngPath)
		if err != nil {
			return fmt.Errorf("create PNG file %q: %w", pngPath, err)
		}
		encErr := png.Encode(f, cs.SheetRGBA)
		closeErr := f.Close()
		if encErr != nil {
			return fmt.Errorf("encode PNG %q: %w", pngPath, encErr)
		}
		if closeErr != nil {
			return closeErr
		}
	}

	if jsonPath != "" {
		if dir := filepath.Dir(jsonPath); dir != "" && dir != "." {
			if err := os.MkdirAll(dir, 0o755); err != nil {
				return fmt.Errorf("create JSON output directory %q: %w", dir, err)
			}
		}
		entries := make([]AsepriteFrameEntry, 0, len(cs.Frames))
		for i := range cs.Frames {
			c := i % cs.SheetCols
			r := i / cs.SheetCols
			dur := 100
			if i < len(cs.FrameDurations) && cs.FrameDurations[i] > 0 {
				dur = cs.FrameDurations[i]
			}
			entries = append(entries, AsepriteFrameEntry{
				Filename: fmt.Sprintf("%s #%d", cs.Title, i),
				Frame: AsepriteRectJSON{
					X: c * cs.FrameW,
					Y: r * cs.FrameH,
					W: cs.FrameW,
					H: cs.FrameH,
				},
				SpriteSourceSize: AsepriteRectJSON{X: 0, Y: 0, W: cs.FrameW, H: cs.FrameH},
				SourceSize:       AsepriteSizeJSON{W: cs.FrameW, H: cs.FrameH},
				Duration:         dur,
			})
		}
		b := cs.SheetRGBA.Bounds()
		manifest := AsepriteSheetJSON{
			Frames: entries,
			Meta: AsepriteMetaJSON{
				App:         "https://skills.danicat.dev/sprite-design",
				Version:     "1.0",
				Image:       filepath.Base(pngPath),
				Format:      "RGBA8888",
				Size:        AsepriteSizeJSON{W: b.Dx(), H: b.Dy()},
				FrameWidth:  cs.FrameW,
				FrameHeight: cs.FrameH,
				Cols:        cs.SheetCols,
				Rows:        cs.SheetRows,
				Scale:       "1",
				FrameTags:   cs.Tags,
			},
		}
		jb, err := json.MarshalIndent(manifest, "", "  ")
		if err != nil {
			return fmt.Errorf("marshal sprite sheet JSON: %w", err)
		}
		if err := os.WriteFile(jsonPath, jb, 0o644); err != nil {
			return fmt.Errorf("write JSON manifest %q: %w", jsonPath, err)
		}
	}
	return nil
}

// NormalizeOptions configures AI/external sprite sheet cleanup and grid alignment.
type NormalizeOptions struct {
	Title           string
	FrameWidth      int
	FrameHeight     int
	GridCols        int           // Optional explicit grid columns per source image (0 = w / FrameWidth)
	GridRows        int           // Optional explicit grid rows per source image (0 = h / FrameHeight)
	ColorTolerance  uint8         // RGB Manhattan tolerance for background key removal (default 18)
	AutoCenterX     bool          // Horizontally center each frame's opaque bounding box
	GroundBottom    bool          // Align bottom of each frame's opaque bounding box to (FrameHeight - BottomPadding)
	BottomPadding   int           // Pixels from bottom when GroundBottom is true (default 1)
	DefaultDuration int           // Frame duration in ms (default 100)
	Tags            []CompiledTag // Optional explicit animation tags
}

func colorDistManhattan(a, b color.RGBA) int {
	dr := int(a.R) - int(b.R)
	if dr < 0 {
		dr = -dr
	}
	dg := int(a.G) - int(b.G)
	if dg < 0 {
		dg = -dg
	}
	db := int(a.B) - int(b.B)
	if db < 0 {
		db = -db
	}
	return dr + dg + db
}

// NormalizeSpriteSheet cleans up a raw AI-generated or external sprite sheet image:
// 1. Detects solid, chroma-key (#00FF00 / #FF00FF), or 2-tone checkerboard background colors and strips them to transparent
// 2. Enforces premultiplied alpha (R, G, B <= A) on all pixels and suppresses green/magenta chroma-key edge spill
// 3. Optionally slices a high-resolution GridCols x GridRows sheet using gutter-aware cell bounds and uniform scaling
// 4. Packs all non-empty frames into a validated CompiledSprite ready for Ebitengine, .aseprite, or GIF export.
func NormalizeSpriteSheet(src image.Image, opts NormalizeOptions) (*CompiledSprite, error) {
	if src == nil {
		return nil, fmt.Errorf("normalize sprite sheet: source image is nil")
	}
	return NormalizeMultiSpriteSheets([]image.Image{src}, opts)
}

// NormalizeMultiSpriteSheets normalizes and combines one or more raw sprite sheet images into a single CompiledSprite.
// If opts.FrameWidth or opts.FrameHeight is <= 0 when GridCols and GridRows are provided, the native cell resolution
// (w / GridCols by h / GridRows) is preserved automatically for 2D HD workflows.
func NormalizeMultiSpriteSheets(srcs []image.Image, opts NormalizeOptions) (*CompiledSprite, error) {
	if len(srcs) == 0 || srcs[0] == nil {
		return nil, fmt.Errorf("normalize sprite sheet: source image is nil")
	}
	if (opts.FrameWidth <= 0 || opts.FrameHeight <= 0) && opts.GridCols > 0 && opts.GridRows > 0 {
		b0 := srcs[0].Bounds()
		if opts.FrameWidth <= 0 {
			opts.FrameWidth = b0.Dx() / opts.GridCols
		}
		if opts.FrameHeight <= 0 {
			opts.FrameHeight = b0.Dy() / opts.GridRows
		}
	}
	if opts.FrameWidth <= 0 || opts.FrameHeight <= 0 {
		return nil, fmt.Errorf("normalize sprite sheet: invalid frame size %dx%d", opts.FrameWidth, opts.FrameHeight)
	}

	tol := int(opts.ColorTolerance)
	if tol <= 0 {
		tol = 18
	}
	dur := opts.DefaultDuration
	if dur <= 0 {
		dur = 100
	}
	title := opts.Title
	if title == "" {
		title = "Normalized Sprite Sheet"
	}

	// Fast path: 1:1 pixel grid when GridCols/GridRows are not specified
	if opts.GridCols <= 0 && opts.GridRows <= 0 {
		var frames []*image.RGBA
		var durations []int

		for _, src := range srcs {
			b := src.Bounds()
			w, h := b.Dx(), b.Dy()
			if w < opts.FrameWidth || h < opts.FrameHeight {
				return nil, fmt.Errorf("normalize sprite sheet: image size %dx%d is smaller than frame size %dx%d",
					w, h, opts.FrameWidth, opts.FrameHeight)
			}
			if w%opts.FrameWidth != 0 || h%opts.FrameHeight != 0 {
				return nil, fmt.Errorf("normalize sprite sheet: image size %dx%d is not divisible by frame size %dx%d",
					w, h, opts.FrameWidth, opts.FrameHeight)
			}

			rgba := toPremultipliedRGBA(src)
			bgKeys := detectBackgroundKeys(rgba, opts.FrameWidth, opts.FrameHeight)
			if len(bgKeys) > 0 {
				stripBackgroundFloodFill(rgba, opts.FrameWidth, opts.FrameHeight, bgKeys, tol)
			}

			cols := w / opts.FrameWidth
			rows := h / opts.FrameHeight
			for r := 0; r < rows; r++ {
				for c := 0; c < cols; c++ {
					cell := image.NewRGBA(image.Rect(0, 0, opts.FrameWidth, opts.FrameHeight))
					minX, minY := opts.FrameWidth, opts.FrameHeight
					maxX, maxY := -1, -1
					opaqueCount := 0

					for fy := 0; fy < opts.FrameHeight; fy++ {
						for fx := 0; fx < opts.FrameWidth; fx++ {
							px := rgba.RGBAAt(c*opts.FrameWidth+fx, r*opts.FrameHeight+fy)
							if px.A > 0 {
								opaqueCount++
								if fx < minX {
									minX = fx
								}
								if fx > maxX {
									maxX = fx
								}
								if fy < minY {
									minY = fy
								}
								if fy > maxY {
									maxY = fy
								}
							}
							cell.SetRGBA(fx, fy, px)
						}
					}

					if opaqueCount == 0 {
						continue
					}

					if opts.AutoCenterX || opts.GroundBottom {
						aligned := image.NewRGBA(image.Rect(0, 0, opts.FrameWidth, opts.FrameHeight))
						shiftX := 0
						if opts.AutoCenterX {
							bboxCenterX := (minX + maxX) / 2
							shiftX = (opts.FrameWidth / 2) - bboxCenterX
						}
						shiftY := 0
						if opts.GroundBottom {
							pad := opts.BottomPadding
							if pad < 0 {
								pad = 1
							}
							targetMaxY := opts.FrameHeight - 1 - pad
							shiftY = targetMaxY - maxY
						}
						for fy := minY; fy <= maxY; fy++ {
							ny := fy + shiftY
							if ny < 0 || ny >= opts.FrameHeight {
								continue
							}
							for fx := minX; fx <= maxX; fx++ {
								nx := fx + shiftX
								if nx < 0 || nx >= opts.FrameWidth {
									continue
								}
								aligned.SetRGBA(nx, ny, cell.RGBAAt(fx, fy))
							}
						}
						cell = aligned
					}

					frames = append(frames, cell)
					durations = append(durations, dur)
				}
			}
		}

		if len(frames) == 0 {
			return nil, fmt.Errorf("normalize sprite sheet: all frames are empty after background removal")
		}
		return packNormalizedSprite(title, opts, frames, durations), nil
	}

	// High-res AI grid path (GridCols x GridRows per source image):
	// 1. Chroma-key + despill each source image
	// 2. Locate gutter-aware row/col cell bounds so tails/paws never clip
	// 3. Measure main character component bounding boxes and resample at a uniform scale into FrameWidth x FrameHeight
	type extractedCell struct {
		img                        *image.RGBA
		fullMinX, fullMinY         int
		fullMaxX, fullMaxY         int
		bodyMinX, bodyMinY         int
		bodyMaxX, bodyMaxY         int
	}
	var rawCells []extractedCell
	maxBodyW := 1
	maxBodyH := 1

	for _, src := range srcs {
		b := src.Bounds()
		w, h := b.Dx(), b.Dy()
		cols := opts.GridCols
		rows := opts.GridRows
		if cols <= 0 {
			cols = 4
		}
		if rows <= 0 {
			rows = 4
		}
		if w < cols || h < rows {
			return nil, fmt.Errorf("normalize sprite sheet: image size %dx%d too small for %dx%d grid", w, h, cols, rows)
		}

		rgba := toPremultipliedRGBA(src)
		stripHighResChromaKey(rgba, cols, rows, tol)

		rowBounds := findOptimalGridSplits(rgba, rows, true)
		colBoundsByRow := make([][]int, rows)
		for r := 0; r < rows; r++ {
			colBoundsByRow[r] = findOptimalColSplitsInRow(rgba, rowBounds[r], rowBounds[r+1], cols)
		}
		for r := 0; r < rows; r++ {
			colBounds := colBoundsByRow[r]
			for c := 0; c < cols; c++ {
				x0, x1 := colBounds[c], colBounds[c+1]
				// Refine row split locally within column [x0, x1] so overhanging limbs in a single column find their own empty gutter
				localRowBounds := findOptimalRowSplitsInCol(rgba, x0, x1, rows)
				y0, y1 := localRowBounds[r], localRowBounds[r+1]
				cw, ch := x1-x0, y1-y0
				if cw <= 0 || ch <= 0 {
					continue
				}
				cellImg := image.NewRGBA(image.Rect(0, 0, cw, ch))
				draw.Draw(cellImg, cellImg.Bounds(), rgba, image.Point{X: x0, Y: y0}, draw.Src)

				fMinX, fMinY, fMaxX, fMaxY, bMinX, bMinY, bMaxX, bMaxY, ok := findMainBodyAndFullBBox(cellImg)
				if !ok {
					continue
				}
				bw := bMaxX - bMinX + 1
				bh := bMaxY - bMinY + 1
				if bw > maxBodyW {
					maxBodyW = bw
				}
				if bh > maxBodyH {
					maxBodyH = bh
				}
				rawCells = append(rawCells, extractedCell{
					img:      cellImg,
					fullMinX: fMinX, fullMinY: fMinY, fullMaxX: fMaxX, fullMaxY: fMaxY,
					bodyMinX: bMinX, bodyMinY: bMinY, bodyMaxX: bMaxX, bodyMaxY: bMaxY,
				})
			}
		}
	}

	if len(rawCells) == 0 {
		return nil, fmt.Errorf("normalize sprite sheet: all grid cells are empty after chroma-key removal")
	}

	pad := opts.BottomPadding
	if pad <= 0 {
		pad = 2
	}
	availW := float64(opts.FrameWidth - pad*2)
	availH := float64(opts.FrameHeight - pad*2)
	if availW < 4 {
		availW = float64(opts.FrameWidth)
	}
	if availH < 4 {
		availH = float64(opts.FrameHeight)
	}
	scaleX := availW / float64(maxBodyW)
	scaleY := availH / float64(maxBodyH)
	uniformScale := math.Min(scaleX, scaleY)
	// When the target resolution is large enough to hold the native HD sprites (>= 128px and uniformScale >= 0.92),
	// lock uniformScale to 1.0 so native 2D HD line-art is copied 1:1 without resampling blur.
	if opts.FrameWidth >= 128 && opts.FrameHeight >= 128 && uniformScale >= 0.92 && uniformScale <= 1.25 {
		uniformScale = 1.0
	}

	var frames []*image.RGBA
	var durations []int
	for idx, rc := range rawCells {
		frame := resampleCellToFrame(rc.img, rc.fullMinX, rc.fullMinY, rc.fullMaxX, rc.fullMaxY,
			rc.bodyMinX, rc.bodyMinY, rc.bodyMaxX, rc.bodyMaxY,
			uniformScale, opts.FrameWidth, opts.FrameHeight, opts.AutoCenterX, opts.GroundBottom, pad, idx, opts.Tags)
		frames = append(frames, frame)
		durations = append(durations, dur)
	}

	return packNormalizedSprite(title, opts, frames, durations), nil
}

func toPremultipliedRGBA(src image.Image) *image.RGBA {
	b := src.Bounds()
	w, h := b.Dx(), b.Dy()
	rgba := image.NewRGBA(image.Rect(0, 0, w, h))
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			r16, g16, b16, a16 := src.At(b.Min.X+x, b.Min.Y+y).RGBA()
			if a16 == 0 {
				rgba.SetRGBA(x, y, color.RGBA{0, 0, 0, 0})
				continue
			}
			r8 := uint8(r16 >> 8)
			g8 := uint8(g16 >> 8)
			b8 := uint8(b16 >> 8)
			a8 := uint8(a16 >> 8)
			if r8 > a8 {
				r8 = a8
			}
			if g8 > a8 {
				g8 = a8
			}
			if b8 > a8 {
				b8 = a8
			}
			rgba.SetRGBA(x, y, color.RGBA{R: r8, G: g8, B: b8, A: a8})
		}
	}
	return rgba
}

func packNormalizedSprite(title string, opts NormalizeOptions, frames []*image.RGBA, durations []int) *CompiledSprite {
	dur := opts.DefaultDuration
	if dur <= 0 {
		dur = 100
	}
	tags := opts.Tags
	if len(tags) == 0 {
		tags = []CompiledTag{
			{
				Name:       "idle",
				FromFrame:  0,
				ToFrame:    len(frames) - 1,
				Frames:     len(frames),
				DurationMs: dur,
				Loop:       "loop",
			},
		}
	} else {
		for _, t := range tags {
			if t.DurationMs > 0 {
				for fi := t.FromFrame; fi <= t.ToFrame && fi < len(durations); fi++ {
					if fi >= 0 {
						durations[fi] = t.DurationMs
					}
				}
			}
		}
	}

	outCols := len(frames)
	if outCols > 8 {
		outCols = 8
	}
	if opts.GridCols > 0 && opts.GridCols <= 8 {
		outCols = opts.GridCols
	}
	outRows := (len(frames) + outCols - 1) / outCols
	sheetRGBA := image.NewRGBA(image.Rect(0, 0, outCols*opts.FrameWidth, outRows*opts.FrameHeight))
	for i, fr := range frames {
		c := i % outCols
		r := i / outCols
		dst := image.Rect(c*opts.FrameWidth, r*opts.FrameHeight, (c+1)*opts.FrameWidth, (r+1)*opts.FrameHeight)
		draw.Draw(sheetRGBA, dst, fr, image.Point{0, 0}, draw.Src)
	}

	return &CompiledSprite{
		Title:          title,
		Type:           "sprite",
		FrameW:         opts.FrameWidth,
		FrameH:         opts.FrameHeight,
		Palette:        "custom",
		Frames:         frames,
		FrameDurations: durations,
		Tags:           tags,
		PaletteColors:  collectUniqueColors(sheetRGBA),
		SheetRGBA:      sheetRGBA,
		SheetCols:      outCols,
		SheetRows:      outRows,
	}
}

func stripHighResChromaKey(img *image.RGBA, cols, rows, tol int) {
	b := img.Bounds()
	w, h := b.Dx(), b.Dy()
	cellW, cellH := w/cols, h/rows
	bgKeys := detectBackgroundKeys(img, cellW, cellH)

	isGreenKey := false
	isMagentaKey := false
	var primaryKey color.RGBA
	if len(bgKeys) > 0 {
		primaryKey = bgKeys[0]
	}
	for _, k := range bgKeys {
		if int(k.G) > 140 && int(k.G)-int(k.R) > 50 && int(k.G)-int(k.B) > 50 {
			isGreenKey = true
			primaryKey = k
		}
		if int(k.R) > 140 && int(k.B) > 140 && int(k.R)-int(k.G) > 50 {
			isMagentaKey = true
			primaryKey = k
		}
	}

	effTol := tol
	if effTol < 36 {
		effTol = 36
	}

	keyGreenExcess := float64(int(primaryKey.G) - maxInt(int(primaryKey.R), int(primaryKey.B)))
	if keyGreenExcess < 120.0 {
		keyGreenExcess = 220.0
	}

	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			c := img.RGBAAt(x, y)
			if c.A == 0 {
				continue
			}
			matched := false
			for _, k := range bgKeys {
				if colorDistManhattan(c, k) <= effTol {
					matched = true
					break
				}
			}
			if isGreenKey {
				maxRB := maxInt(int(c.R), int(c.B))
				gExcess := float64(int(c.G) - maxRB)
				if matched || (int(c.G) > 85 && gExcess >= keyGreenExcess*0.52) {
					img.SetRGBA(x, y, color.RGBA{0, 0, 0, 0})
					continue
				}
				if gExcess > 2.0 {
					// Smooth premultiplied alpha chroma unmixing for anti-aliased 2D HD outlines
					bgWeight := math.Min(0.95, gExcess/(keyGreenExcess*0.55))
					alpha := 1.0 - bgWeight*0.85
					fgR := math.Max(0.0, float64(c.R)-bgWeight*float64(primaryKey.R))
					fgB := math.Max(0.0, float64(c.B)-bgWeight*float64(primaryKey.B))
					fgG := float64(maxRB) * 0.85
					pmA := clampUint8(int(math.Round(255.0 * alpha)))
					pmR := clampUint8(int(math.Round(fgR * alpha)))
					pmG := clampUint8(int(math.Round(fgG * alpha)))
					pmB := clampUint8(int(math.Round(fgB * alpha)))
					if pmR > pmA {
						pmR = pmA
					}
					if pmG > pmA {
						pmG = pmA
					}
					if pmB > pmA {
						pmB = pmA
					}
					img.SetRGBA(x, y, color.RGBA{R: pmR, G: pmG, B: pmB, A: pmA})
				}
				continue
			}

			if !matched && isMagentaKey {
				minRB := int(c.R)
				if int(c.B) < minRB {
					minRB = int(c.B)
				}
				if minRB > 95 && minRB-int(c.G) > 26 {
					matched = true
				}
			}
			if matched {
				img.SetRGBA(x, y, color.RGBA{0, 0, 0, 0})
			} else if isMagentaKey {
				if int(c.R) > int(c.G)+25 && int(c.B) > int(c.G)+25 {
					c.R = c.G
					c.B = c.G
					img.SetRGBA(x, y, c)
				}
			}
		}
	}
}

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func findOptimalGridSplits(img *image.RGBA, count int, horizontal bool) []int {
	b := img.Bounds()
	w, h := b.Dx(), b.Dy()
	total := w
	if horizontal {
		total = h
	}
	splits := make([]int, count+1)
	splits[0] = 0
	splits[count] = total
	step := float64(total) / float64(count)
	searchRadius := int(step * 0.22)

	for i := 1; i < count; i++ {
		nominal := int(math.Round(float64(i) * step))
		bestPos := nominal
		bestScore := 1 << 30
		bestDist := 1 << 30
		for pos := nominal - searchRadius; pos <= nominal+searchRadius; pos++ {
			if pos <= splits[i-1]+8 || pos >= total-8 {
				continue
			}
			opaque := 0
			if horizontal {
				for x := 0; x < w; x++ {
					if img.RGBAAt(x, pos).A > 0 {
						opaque++
					}
				}
			} else {
				for y := 0; y < h; y++ {
					if img.RGBAAt(pos, y).A > 0 {
						opaque++
					}
				}
			}
			dist := pos - nominal
			if dist < 0 {
				dist = -dist
			}
			if opaque < bestScore || (opaque == bestScore && dist < bestDist) {
				bestScore = opaque
				bestDist = dist
				bestPos = pos
			}
		}
		splits[i] = bestPos
	}
	return splits
}

func findOptimalColSplitsInRow(img *image.RGBA, y0, y1, cols int) []int {
	b := img.Bounds()
	w := b.Dx()
	splits := make([]int, cols+1)
	splits[0] = 0
	splits[cols] = w
	step := float64(w) / float64(cols)
	searchRadius := int(step * 0.22)

	for i := 1; i < cols; i++ {
		nominal := int(math.Round(float64(i) * step))
		bestPos := nominal
		bestScore := 1 << 30
		bestDist := 1 << 30
		for pos := nominal - searchRadius; pos <= nominal+searchRadius; pos++ {
			if pos <= splits[i-1]+8 || pos >= w-8 {
				continue
			}
			opaque := 0
			for y := y0; y < y1; y++ {
				if img.RGBAAt(pos, y).A > 0 {
					opaque++
				}
			}
			dist := pos - nominal
			if dist < 0 {
				dist = -dist
			}
			if opaque < bestScore || (opaque == bestScore && dist < bestDist) {
				bestScore = opaque
				bestDist = dist
				bestPos = pos
			}
		}
		splits[i] = bestPos
	}
	return splits
}

func findOptimalRowSplitsInCol(img *image.RGBA, x0, x1, rows int) []int {
	b := img.Bounds()
	h := b.Dy()
	splits := make([]int, rows+1)
	splits[0] = 0
	splits[rows] = h
	step := float64(h) / float64(rows)
	searchRadius := int(step * 0.24)

	for i := 1; i < rows; i++ {
		nominal := int(math.Round(float64(i) * step))
		bestPos := nominal
		bestScore := 1 << 30
		bestDist := 1 << 30
		for pos := nominal - searchRadius; pos <= nominal+searchRadius; pos++ {
			if pos <= splits[i-1]+8 || pos >= h-8 {
				continue
			}
			opaque := 0
			for x := x0; x < x1; x++ {
				if img.RGBAAt(x, pos).A > 0 {
					opaque++
				}
			}
			dist := pos - nominal
			if dist < 0 {
				dist = -dist
			}
			if opaque < bestScore || (opaque == bestScore && dist < bestDist) {
				bestScore = opaque
				bestDist = dist
				bestPos = pos
			}
		}
		splits[i] = bestPos
	}
	return splits
}

func findMainBodyAndFullBBox(cell *image.RGBA) (fMinX, fMinY, fMaxX, fMaxY, bMinX, bMinY, bMaxX, bMaxY int, ok bool) {
	b := cell.Bounds()
	w, h := b.Dx(), b.Dy()
	visited := make([]bool, w*h)

	type comp struct {
		pixels             [][2]int
		minX, minY         int
		maxX, maxY         int
	}
	var comps []comp
	dirs := [8][2]int{{-1, 0}, {1, 0}, {0, -1}, {0, 1}, {-1, -1}, {1, -1}, {-1, 1}, {1, 1}}

	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			idx := y*w + x
			if visited[idx] || cell.RGBAAt(x, y).A == 0 {
				continue
			}
			visited[idx] = true
			c := comp{
				minX: x, maxX: x,
				minY: y, maxY: y,
			}
			q := [][2]int{{x, y}}
			for len(q) > 0 {
				pt := q[0]
				q = q[1:]
				c.pixels = append(c.pixels, pt)
				if pt[0] < c.minX {
					c.minX = pt[0]
				}
				if pt[0] > c.maxX {
					c.maxX = pt[0]
				}
				if pt[1] < c.minY {
					c.minY = pt[1]
				}
				if pt[1] > c.maxY {
					c.maxY = pt[1]
				}
				for _, d := range dirs {
					nx, ny := pt[0]+d[0], pt[1]+d[1]
					if nx >= 0 && nx < w && ny >= 0 && ny < h {
						nIdx := ny*w + nx
						if !visited[nIdx] && cell.RGBAAt(nx, ny).A > 0 {
							visited[nIdx] = true
							q = append(q, [2]int{nx, ny})
						}
					}
				}
			}
			comps = append(comps, c)
		}
	}

	if len(comps) == 0 {
		return 0, 0, 0, 0, 0, 0, 0, 0, false
	}

	sort.Slice(comps, func(i, j int) bool {
		return len(comps[i].pixels) > len(comps[j].pixels)
	})
	mainComp := comps[0]
	if len(mainComp.pixels) < 8 {
		return 0, 0, 0, 0, 0, 0, 0, 0, false
	}

	fMinX, fMinY = mainComp.minX, mainComp.minY
	fMaxX, fMaxY = mainComp.maxX, mainComp.maxY
	bMinX, bMinY = mainComp.minX, mainComp.minY
	bMaxX, bMaxY = mainComp.maxX, mainComp.maxY

	borderMargin := maxInt(4, minInt(w, h)/28)
	for i := 1; i < len(comps); i++ {
		cp := comps[i]
		touchesBorder := cp.minY <= borderMargin || cp.maxY >= h-1-borderMargin || cp.minX <= borderMargin || cp.maxX >= w-1-borderMargin
		// Erase tiny isolated noise specks OR disconnected neighboring-cell boundary bleed near the cell edge
		if len(cp.pixels) <= 8 || (touchesBorder && len(cp.pixels)*8 < len(mainComp.pixels)) {
			for _, pt := range cp.pixels {
				cell.SetRGBA(pt[0], pt[1], color.RGBA{0, 0, 0, 0})
			}
			continue
		}
		if cp.minX < fMinX {
			fMinX = cp.minX
		}
		if cp.maxX > fMaxX {
			fMaxX = cp.maxX
		}
		if cp.minY < fMinY {
			fMinY = cp.minY
		}
		if cp.maxY > fMaxY {
			fMaxY = cp.maxY
		}
		// Include in body bounding box only if substantial (>10% of main body)
		if len(cp.pixels)*10 >= len(mainComp.pixels) {
			if cp.minX < bMinX {
				bMinX = cp.minX
			}
			if cp.maxX > bMaxX {
				bMaxX = cp.maxX
			}
			if cp.minY < bMinY {
				bMinY = cp.minY
			}
			if cp.maxY > bMaxY {
				bMaxY = cp.maxY
			}
		}
	}

	return fMinX, fMinY, fMaxX, fMaxY, bMinX, bMinY, bMaxX, bMaxY, true
}

func resampleCellToFrame(
	cell *image.RGBA,
	fMinX, fMinY, fMaxX, fMaxY int,
	bMinX, bMinY, bMaxX, bMaxY int,
	scale float64,
	targetW, targetH int,
	centerX, groundBottom bool,
	pad int,
	frameIdx int,
	tags []CompiledTag,
) *image.RGBA {
	out := image.NewRGBA(image.Rect(0, 0, targetW, targetH))
	if scale <= 0 {
		scale = 1.0
	}

	bodyCenterX := float64(bMinX+bMaxX+1) * 0.5
	bodyCenterY := float64(bMinY+bMaxY+1) * 0.5
	bodyBottomY := float64(bMaxY + 1)

	dstCenterX := float64(targetW) * 0.5
	dstBottomY := float64(targetH - pad)
	dstCenterY := float64(targetH) * 0.5

	// Determine if this frame belongs to an airborne jump/fall tag to preserve vertical arc
	airborneOffsetY := 0.0
	for _, t := range tags {
		if frameIdx >= t.FromFrame && frameIdx <= t.ToFrame {
			tName := strings.ToLower(t.Name)
			localIdx := frameIdx - t.FromFrame
			span := t.ToFrame - t.FromFrame
			if tName == "jump" && span >= 2 {
				frac := float64(localIdx) / float64(span)
				airborneOffsetY = -math.Sin(frac*math.Pi*0.75) * float64(targetH) * 0.14
			} else if tName == "fall" && span >= 2 {
				frac := float64(localIdx) / float64(span)
				airborneOffsetY = -(1.0 - frac) * float64(targetH) * 0.14
			}
			break
		}
	}

	cellBounds := cell.Bounds()
	cw, ch := cellBounds.Dx(), cellBounds.Dy()

	// Exact 1:1 native HD pixel copy when scale == 1.0 (zero resampling blur)
	if math.Abs(scale-1.0) < 1e-4 {
		shiftX := 0
		if centerX {
			shiftX = int(math.Round(dstCenterX - bodyCenterX))
		}
		shiftY := 0
		if groundBottom {
			shiftY = int(math.Round(dstBottomY + airborneOffsetY - bodyBottomY))
		} else {
			shiftY = int(math.Round(dstCenterY - bodyCenterY))
		}
		for sy := fMinY; sy <= fMaxY; sy++ {
			if sy < 0 || sy >= ch {
				continue
			}
			dy := sy + shiftY
			if dy < 0 || dy >= targetH {
				continue
			}
			for sx := fMinX; sx <= fMaxX; sx++ {
				if sx < 0 || sx >= cw {
					continue
				}
				dx := sx + shiftX
				if dx < 0 || dx >= targetW {
					continue
				}
				px := cell.RGBAAt(sx, sy)
				if px.A > 0 {
					out.SetRGBA(dx, dy, px)
				}
			}
		}
		return out
	}

	invScale := 1.0 / scale
	filterRad := math.Max(0.5, invScale*0.5)
	isHD := targetW >= 128 && targetH >= 128

	for dy := 0; dy < targetH; dy++ {
		var srcCenterY float64
		if groundBottom {
			srcCenterY = bodyBottomY - (dstBottomY+airborneOffsetY-(float64(dy)+0.5))*invScale
		} else {
			srcCenterY = bodyCenterY + ((float64(dy)+0.5)-dstCenterY)*invScale
		}
		sy0 := int(math.Floor(srcCenterY - filterRad))
		sy1 := int(math.Ceil(srcCenterY + filterRad))
		if sy1 < fMinY || sy0 > fMaxY {
			continue
		}
		if sy0 < 0 {
			sy0 = 0
		}
		if sy1 >= ch {
			sy1 = ch - 1
		}

		for dx := 0; dx < targetW; dx++ {
			var srcCenterX float64
			if centerX {
				srcCenterX = bodyCenterX + ((float64(dx)+0.5)-dstCenterX)*invScale
			} else {
				srcCenterX = (float64(dx) + 0.5) * invScale
			}
			sx0 := int(math.Floor(srcCenterX - filterRad))
			sx1 := int(math.Ceil(srcCenterX + filterRad))
			if sx1 < fMinX || sx0 > fMaxX {
				continue
			}
			if sx0 < 0 {
				sx0 = 0
			}
			if sx1 >= cw {
				sx1 = cw - 1
			}

			var sumR, sumG, sumB, sumA, count float64
			for sy := sy0; sy <= sy1; sy++ {
				for sx := sx0; sx <= sx1; sx++ {
					px := cell.RGBAAt(sx, sy)
					count += 1.0
					if px.A > 0 {
						sumR += float64(px.R)
						sumG += float64(px.G)
						sumB += float64(px.B)
						sumA += float64(px.A)
					}
				}
			}
			if sumA <= 0 || count <= 0 {
				continue
			}
			avgA := sumA / count
			if isHD {
				// Preserve smooth anti-aliased premultiplied alpha for 2D HD sprites
				a8 := clampUint8(int(math.Round(avgA)))
				if a8 < 8 {
					continue
				}
				r8 := clampUint8(int(math.Round(sumR / count)))
				g8 := clampUint8(int(math.Round(sumG / count)))
				b8 := clampUint8(int(math.Round(sumB / count)))
				if r8 > a8 {
					r8 = a8
				}
				if g8 > a8 {
					g8 = a8
				}
				if b8 > a8 {
					b8 = a8
				}
				out.SetRGBA(dx, dy, color.RGBA{R: r8, G: g8, B: b8, A: a8})
			} else {
				// Crisp alpha threshold for low-res pixel art (< 128px)
				if avgA < 110.0 {
					continue
				}
				r8 := clampUint8(int(math.Round(sumR / (sumA / 255.0))))
				g8 := clampUint8(int(math.Round(sumG / (sumA / 255.0))))
				b8 := clampUint8(int(math.Round(sumB / (sumA / 255.0))))
				out.SetRGBA(dx, dy, color.RGBA{R: r8, G: g8, B: b8, A: 255})
			}
		}
	}
	return out
}

// ParseNormalizeTagFlag parses a CLI "-tag name:from:to[:duration_ms[:loop]]" string into a CompiledTag.
func ParseNormalizeTagFlag(spec string, defaultDur int) (CompiledTag, error) {
	parts := strings.Split(strings.TrimSpace(spec), ":")
	if len(parts) < 3 || len(parts) > 5 {
		return CompiledTag{}, fmt.Errorf("invalid -tag %q: expected format name:from:to[:duration_ms[:loop]]", spec)
	}
	name := strings.TrimSpace(parts[0])
	if name == "" {
		return CompiledTag{}, fmt.Errorf("invalid -tag %q: empty tag name", spec)
	}
	fromIdx, err := strconv.Atoi(strings.TrimSpace(parts[1]))
	if err != nil {
		return CompiledTag{}, fmt.Errorf("invalid -tag %q start frame: %w", spec, err)
	}
	toIdx, err := strconv.Atoi(strings.TrimSpace(parts[2]))
	if err != nil {
		return CompiledTag{}, fmt.Errorf("invalid -tag %q end frame: %w", spec, err)
	}
	if fromIdx < 0 || toIdx < fromIdx {
		return CompiledTag{}, fmt.Errorf("invalid -tag %q range %d..%d", spec, fromIdx, toIdx)
	}
	dur := defaultDur
	if dur <= 0 {
		dur = 100
	}
	if len(parts) >= 4 && strings.TrimSpace(parts[3]) != "" {
		d, err := strconv.Atoi(strings.TrimSpace(parts[3]))
		if err != nil || d <= 0 {
			return CompiledTag{}, fmt.Errorf("invalid -tag %q duration_ms %q", spec, parts[3])
		}
		dur = d
	}
	loop := "forward"
	if len(parts) == 5 && strings.TrimSpace(parts[4]) != "" {
		loop = strings.ToLower(strings.TrimSpace(parts[4]))
	}
	return CompiledTag{
		Name:       name,
		FromFrame:  fromIdx,
		ToFrame:    toIdx,
		Frames:     toIdx - fromIdx + 1,
		DurationMs: dur,
		Loop:       loop,
	}, nil
}

func detectBackgroundKeys(img *image.RGBA, frameW, frameH int) []color.RGBA {
	b := img.Bounds()
	w, h := b.Dx(), b.Dy()
	counts := make(map[color.RGBA]int)
	cols := w / frameW
	rows := h / frameH

	// Sample corners and immediate neighbors of each frame cell
	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			ox, oy := c*frameW, r*frameH
			samplePts := [][2]int{
				{ox, oy}, {ox + 1, oy}, {ox, oy + 1},
				{ox + frameW - 1, oy}, {ox + frameW - 2, oy},
				{ox, oy + frameH - 1}, {ox + frameW - 1, oy + frameH - 1},
			}
			for _, pt := range samplePts {
				if pt[0] >= 0 && pt[0] < w && pt[1] >= 0 && pt[1] < h {
					px := img.RGBAAt(pt[0], pt[1])
					if px.A == 0 {
						// Already transparent background
						return nil
					}
					counts[px]++
				}
			}
		}
	}

	type kv struct {
		col   color.RGBA
		count int
	}
	var sorted []kv
	for col, cnt := range counts {
		sorted = append(sorted, kv{col, cnt})
	}
	sort.Slice(sorted, func(i, j int) bool { return sorted[i].count > sorted[j].count })

	var keys []color.RGBA
	for i := 0; i < len(sorted) && i < 2; i++ {
		keys = append(keys, sorted[i].col)
	}
	return keys
}

func stripBackgroundFloodFill(img *image.RGBA, frameW, frameH int, bgKeys []color.RGBA, tol int) {
	b := img.Bounds()
	w, h := b.Dx(), b.Dy()
	cols := w / frameW
	rows := h / frameH

	matchesBG := func(c color.RGBA) bool {
		if c.A == 0 {
			return true
		}
		for _, k := range bgKeys {
			if colorDistManhattan(c, k) <= tol {
				return true
			}
		}
		return false
	}

	for r := 0; r < rows; r++ {
		for c := 0; c < cols; c++ {
			ox, oy := c*frameW, r*frameH
			visited := make([]bool, frameW*frameH)
			queue := make([][2]int, 0, frameW*2+frameH*2)

			enqueue := func(lx, ly int) {
				if lx < 0 || lx >= frameW || ly < 0 || ly >= frameH {
					return
				}
				idx := ly*frameW + lx
				if visited[idx] {
					return
				}
				if matchesBG(img.RGBAAt(ox+lx, oy+ly)) {
					visited[idx] = true
					queue = append(queue, [2]int{lx, ly})
				}
			}

			// Seed flood fill from all 4 border edges of the frame cell
			for x := 0; x < frameW; x++ {
				enqueue(x, 0)
				enqueue(x, frameH-1)
			}
			for y := 0; y < frameH; y++ {
				enqueue(0, y)
				enqueue(frameW-1, y)
			}

			for len(queue) > 0 {
				pt := queue[0]
				queue = queue[1:]
				img.SetRGBA(ox+pt[0], oy+pt[1], color.RGBA{0, 0, 0, 0})
				enqueue(pt[0]-1, pt[1])
				enqueue(pt[0]+1, pt[1])
				enqueue(pt[0], pt[1]-1)
				enqueue(pt[0], pt[1]+1)
			}
		}
	}
}

// ExtractPaletteRamps samples opaque pixels from a reference character sheet image,
// groups their hues into maxRamps clusters, and builds 4-step MaterialRamps (shadow, base, light, spec)
// ready to paste into a .sprite file.
func ExtractPaletteRamps(src image.Image, maxRamps int) ([]NamedRamp, error) {
	if src == nil {
		return nil, fmt.Errorf("extract palette ramps: source image is nil")
	}
	if maxRamps <= 0 {
		maxRamps = 4
	}
	if maxRamps > 12 {
		maxRamps = 12
	}

	type samplePx struct {
		col color.RGBA
		hue float64
		sat float64
		lum float64
	}

	b := src.Bounds()
	seen := make(map[color.RGBA]int)
	for y := b.Min.Y; y < b.Max.Y; y++ {
		for x := b.Min.X; x < b.Max.X; x++ {
			r16, g16, b16, a16 := src.At(x, y).RGBA()
			if a16 < 0x8000 {
				continue
			}
			c := PremultiplyRGBA(uint8(r16>>8), uint8(g16>>8), uint8(b16>>8), 255)
			// Quantize slightly to merge compression noise
			qc := color.RGBA{R: c.R & 0xF8, G: c.G & 0xF8, B: c.B & 0xF8, A: 255}
			seen[qc]++
		}
	}

	if len(seen) == 0 {
		return nil, fmt.Errorf("extract palette ramps: image contains no opaque pixels")
	}

	samples := make([]samplePx, 0, len(seen))
	for c := range seen {
		h, s, l := rgbToHSL(c.R, c.G, c.B)
		samples = append(samples, samplePx{col: c, hue: h, sat: s, lum: l})
	}

	// Group into maxRamps hue/saturation buckets
	buckets := make([][]samplePx, maxRamps)
	for _, sp := range samples {
		var bIdx int
		if sp.sat < 0.12 && maxRamps > 1 {
			bIdx = 0 // Achromatic/neutral ramp in slot 0
		} else {
			activeBins := maxRamps
			offset := 0
			if maxRamps > 1 {
				activeBins = maxRamps - 1
				offset = 1
			}
			bIdx = offset + (int(math.Floor(sp.hue*float64(activeBins))) % activeBins)
		}
		buckets[bIdx] = append(buckets[bIdx], sp)
	}

	rampNames := []string{"primary", "secondary", "accent", "highlight", "mat5", "mat6", "mat7", "mat8", "mat9", "mat10", "mat11", "mat12"}
	var result []NamedRamp
	nameIdx := 0

	for _, group := range buckets {
		if len(group) == 0 {
			continue
		}
		sort.Slice(group, func(i, j int) bool {
			return group[i].lum < group[j].lum
		})
		baseCol := group[len(group)/2].col
		var mr MaterialRamp
		if len(group) >= 4 {
			mr[0] = group[len(group)*1/8].col
			mr[1] = group[len(group)*3/8].col
			mr[2] = group[len(group)*5/8].col
			mr[3] = group[len(group)*7/8].col
		} else {
			// Synthesize 4 distinct luminance steps around baseCol
			factors := [4]float64{0.45, 0.80, 1.15, 1.45}
			for s := 0; s < 4; s++ {
				mr[s] = PremultiplyRGBA(
					clampUint8(int(float64(baseCol.R)*factors[s])),
					clampUint8(int(float64(baseCol.G)*factors[s])),
					clampUint8(int(float64(baseCol.B)*factors[s])),
					255,
				)
			}
		}

		rName := rampNames[nameIdx%len(rampNames)]
		nameIdx++
		result = append(result, NamedRamp{
			Name: rName,
			Steps: [4]string{
				FormatHexColor(mr[0]),
				FormatHexColor(mr[1]),
				FormatHexColor(mr[2]),
				FormatHexColor(mr[3]),
			},
			Ramp: mr,
		})
	}

	return result, nil
}

func rgbToHSL(r, g, b uint8) (float64, float64, float64) {
	rf := float64(r) / 255.0
	gf := float64(g) / 255.0
	bf := float64(b) / 255.0
	maxC := math.Max(rf, math.Max(gf, bf))
	minC := math.Min(rf, math.Min(gf, bf))
	l := (maxC + minC) * 0.5
	if maxC == minC {
		return 0, 0, l
	}
	d := maxC - minC
	var s float64
	if l > 0.5 {
		s = d / (2.0 - maxC - minC)
	} else {
		s = d / (maxC + minC)
	}
	var h float64
	switch maxC {
	case rf:
		h = (gf - bf) / d
		if gf < bf {
			h += 6.0
		}
	case gf:
		h = (bf-rf)/d + 2.0
	case bf:
		h = (rf-gf)/d + 4.0
	}
	h /= 6.0
	return h, s, l
}

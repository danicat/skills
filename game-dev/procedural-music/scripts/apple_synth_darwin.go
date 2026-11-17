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

//go:build darwin

package main

/*
#cgo LDFLAGS: -framework AudioToolbox -framework CoreAudio -framework CoreFoundation

#include <AudioToolbox/AudioToolbox.h>
#include <CoreFoundation/CoreFoundation.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
	AudioComponentInstance synthUnit;
	AudioBufferList*       bufferList;
	float*                 leftBuf;
	float*                 rightBuf;
	UInt32                 maxFrames;
	Float64                sampleTime;
} AppleSynthContext;

static OSStatus initAppleSynth(AppleSynthContext* ctx, const char* bankPath, double sampleRate, UInt32 maxFrames) {
	memset(ctx, 0, sizeof(AppleSynthContext));
	ctx->maxFrames = maxFrames;

	AudioComponentDescription desc;
	memset(&desc, 0, sizeof(desc));
	desc.componentType = kAudioUnitType_MusicDevice;
	desc.componentSubType = kAudioUnitSubType_MIDISynth;
	desc.componentManufacturer = kAudioUnitManufacturer_Apple;

	AudioComponent comp = AudioComponentFindNext(NULL, &desc);
	if (comp == NULL) {
		desc.componentSubType = kAudioUnitSubType_DLSSynth;
		comp = AudioComponentFindNext(NULL, &desc);
		if (comp == NULL) {
			return -1;
		}
	}

	OSStatus status = AudioComponentInstanceNew(comp, &ctx->synthUnit);
	if (status != noErr) {
		return status;
	}

	if (bankPath != NULL && strlen(bankPath) > 0) {
		CFURLRef bankURL = CFURLCreateFromFileSystemRepresentation(
			kCFAllocatorDefault,
			(const UInt8*)bankPath,
			(CFIndex)strlen(bankPath),
			false
		);
		if (bankURL == NULL) {
			AudioComponentInstanceDispose(ctx->synthUnit);
			ctx->synthUnit = NULL;
			return -2;
		}
		status = AudioUnitSetProperty(
			ctx->synthUnit,
			kMusicDeviceProperty_SoundBankURL,
			kAudioUnitScope_Global,
			0,
			&bankURL,
			sizeof(bankURL)
		);
		CFRelease(bankURL);
		if (status != noErr) {
			AudioComponentInstanceDispose(ctx->synthUnit);
			ctx->synthUnit = NULL;
			return status;
		}
	}

	UInt32 offline = 1;
	AudioUnitSetProperty(
		ctx->synthUnit,
		kAudioUnitProperty_OfflineRender,
		kAudioUnitScope_Global,
		0,
		&offline,
		sizeof(offline)
	);

	UInt32 usesReverb = 0;
	AudioUnitSetProperty(
		ctx->synthUnit,
		kAudioUnitProperty_UsesInternalReverb,
		kAudioUnitScope_Global,
		0,
		&usesReverb,
		sizeof(usesReverb)
	);

	status = AudioUnitSetProperty(
		ctx->synthUnit,
		kAudioUnitProperty_MaximumFramesPerSlice,
		kAudioUnitScope_Global,
		0,
		&maxFrames,
		sizeof(maxFrames)
	);
	if (status != noErr) {
		AudioComponentInstanceDispose(ctx->synthUnit);
		ctx->synthUnit = NULL;
		return status;
	}

	AudioStreamBasicDescription streamFormat;
	memset(&streamFormat, 0, sizeof(streamFormat));
	streamFormat.mSampleRate = sampleRate;
	streamFormat.mFormatID = kAudioFormatLinearPCM;
	streamFormat.mFormatFlags = kAudioFormatFlagsNativeFloatPacked | kAudioFormatFlagIsNonInterleaved;
	streamFormat.mBytesPerPacket = sizeof(float);
	streamFormat.mFramesPerPacket = 1;
	streamFormat.mBytesPerFrame = sizeof(float);
	streamFormat.mChannelsPerFrame = 2;
	streamFormat.mBitsPerChannel = 32;

	status = AudioUnitSetProperty(
		ctx->synthUnit,
		kAudioUnitProperty_StreamFormat,
		kAudioUnitScope_Output,
		0,
		&streamFormat,
		sizeof(streamFormat)
	);
	if (status != noErr) {
		AudioComponentInstanceDispose(ctx->synthUnit);
		ctx->synthUnit = NULL;
		return status;
	}

	status = AudioUnitInitialize(ctx->synthUnit);
	if (status != noErr) {
		AudioComponentInstanceDispose(ctx->synthUnit);
		ctx->synthUnit = NULL;
		return status;
	}

	ctx->leftBuf = (float*)calloc(maxFrames, sizeof(float));
	ctx->rightBuf = (float*)calloc(maxFrames, sizeof(float));
	ctx->bufferList = (AudioBufferList*)calloc(1, offsetof(AudioBufferList, mBuffers) + (2 * sizeof(AudioBuffer)));
	if (ctx->leftBuf == NULL || ctx->rightBuf == NULL || ctx->bufferList == NULL) {
		AudioUnitUninitialize(ctx->synthUnit);
		AudioComponentInstanceDispose(ctx->synthUnit);
		ctx->synthUnit = NULL;
		free(ctx->leftBuf);
		free(ctx->rightBuf);
		free(ctx->bufferList);
		return -3;
	}

	ctx->bufferList->mNumberBuffers = 2;
	ctx->bufferList->mBuffers[0].mNumberChannels = 1;
	ctx->bufferList->mBuffers[0].mDataByteSize = maxFrames * sizeof(float);
	ctx->bufferList->mBuffers[0].mData = ctx->leftBuf;
	ctx->bufferList->mBuffers[1].mNumberChannels = 1;
	ctx->bufferList->mBuffers[1].mDataByteSize = maxFrames * sizeof(float);
	ctx->bufferList->mBuffers[1].mData = ctx->rightBuf;

	return noErr;
}

static OSStatus sendMIDIEvent(AppleSynthContext* ctx, UInt32 status, UInt32 data1, UInt32 data2, UInt32 offsetSample) {
	return MusicDeviceMIDIEvent(ctx->synthUnit, status, data1, data2, offsetSample);
}

static OSStatus renderSlice(AppleSynthContext* ctx, UInt32 numFrames) {
	AudioUnitRenderActionFlags flags = 0;
	AudioTimeStamp timeStamp;
	memset(&timeStamp, 0, sizeof(timeStamp));
	timeStamp.mSampleTime = ctx->sampleTime;
	timeStamp.mFlags = kAudioTimeStampSampleTimeValid;

	ctx->bufferList->mBuffers[0].mDataByteSize = numFrames * sizeof(float);
	ctx->bufferList->mBuffers[1].mDataByteSize = numFrames * sizeof(float);
	memset(ctx->leftBuf, 0, numFrames * sizeof(float));
	memset(ctx->rightBuf, 0, numFrames * sizeof(float));

	OSStatus status = AudioUnitRender(ctx->synthUnit, &flags, &timeStamp, 0, numFrames, ctx->bufferList);
	if (status == noErr) {
		ctx->sampleTime += (Float64)numFrames;
	}
	return status;
}

static void closeAppleSynth(AppleSynthContext* ctx) {
	if (ctx->synthUnit != NULL) {
		AudioUnitUninitialize(ctx->synthUnit);
		AudioComponentInstanceDispose(ctx->synthUnit);
		ctx->synthUnit = NULL;
	}
	if (ctx->leftBuf != NULL) {
		free(ctx->leftBuf);
		ctx->leftBuf = NULL;
	}
	if (ctx->rightBuf != NULL) {
		free(ctx->rightBuf);
		ctx->rightBuf = NULL;
	}
	if (ctx->bufferList != NULL) {
		free(ctx->bufferList);
		ctx->bufferList = NULL;
	}
}
*/
import "C"

import (
	"fmt"
	"math"
	"os"
	"sort"
	"sync"
	"unsafe"
)

const defaultAppleDLSSoundBank = "/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls"

var appleAudioUnitInitMu sync.Mutex

type scheduledMIDIEvent struct {
	sampleOffset int
	order        int // 0 = NoteOff, 1 = Program/CC/PitchBend, 2 = NoteOn
	status       uint8
	data1        uint8
	data2        uint8
}

// SynthesizeScoreApple renders a parsed Score offline using macOS's native AudioToolbox
// MIDISynth / DLSSynth AudioUnit backed by Apple's built-in Roland GS / General MIDI real
// instrument bank (gs_instruments.dls). Each track is rendered continuously on its own
// isolated AudioUnit with natural NoteOff release tails, preserving 100% of Apple's real
// instrument timbre while following the score's dynamic arrangement and stereo panning.
func SynthesizeScoreApple(score *Score) ([]byte, error) {
	mixed, _, err := SynthesizeScoreAppleWithStems(score)
	return mixed, err
}

// SynthesizeScoreAppleWithStems renders a parsed Score offline using macOS's native AudioToolbox
// MIDISynth / DLSSynth AudioUnit backed by Apple's built-in Roland GS / General MIDI real
// instrument bank (gs_instruments.dls), returning both the mixed stereo PCM and per-track stems.
func SynthesizeScoreAppleWithStems(score *Score) ([]byte, [][]byte, error) {
	if score == nil || len(score.Tracks) == 0 {
		return nil, nil, fmt.Errorf("synthesize apple score: score is nil or has no tracks")
	}

	bankPath := defaultAppleDLSSoundBank
	if _, err := os.Stat(bankPath); err != nil {
		return nil, nil, fmt.Errorf("synthesize apple score: macOS system soundbank %q not found: %w", bankPath, err)
	}

	var maxSamples int
	for _, tr := range score.Tracks {
		var trSec float64
		for _, ev := range tr.Events {
			if ev.DurationSec > 0 {
				trSec += ev.DurationSec
			}
		}
		n := int(math.Round(trSec * SampleRate))
		if n > maxSamples {
			maxSamples = n
		}
	}
	if maxSamples <= 0 {
		return nil, nil, fmt.Errorf("synthesize apple score: score has 0 total samples")
	}

	trackPCMs := make([][]byte, len(score.Tracks))
	trackErrs := make([]error, len(score.Tracks))
	var wg sync.WaitGroup

	for trIdx, tr := range score.Tracks {
		wg.Add(1)
		go func(idx int, track Track) {
			defer wg.Done()
			pcm, err := renderAppleSingleTrack(track, bankPath, maxSamples)
			if err != nil {
				trackErrs[idx] = err
				return
			}
			trackPCMs[idx] = pcm
		}(trIdx, tr)
	}
	wg.Wait()

	for _, err := range trackErrs {
		if err != nil {
			return nil, nil, err
		}
	}

	mixed := MixTracksPCM(trackPCMs)
	var err error
	mixed, err = applyScorePostFX(mixed, score)
	if err != nil {
		return nil, nil, err
	}

	for i := range trackPCMs {
		if len(trackPCMs[i]) > 0 {
			stemOut, stemErr := applyScorePostFX(trackPCMs[i], score)
			if stemErr == nil {
				trackPCMs[i] = stemOut
			}
		}
	}

	return mixed, trackPCMs, nil
}

func renderAppleSingleTrack(tr Track, bankPath string, totalSamples int) ([]byte, error) {
	const melCh uint8 = 0
	const drumChannel uint8 = 9

	var midiEvents []scheduledMIDIEvent
	initialProg := -1
	lastProg := -1
	lastModWheel := -1
	cursorSec := 0.0

	for _, ev := range tr.Events {
		if ev.DurationSec <= 0 {
			continue
		}
		startSample := int(math.Round(cursorSec * SampleRate))
		cursorSec += ev.DurationSec
		endSample := int(math.Round(cursorSec * SampleRate))
		if endSample > totalSamples {
			endSample = totalSamples
		}
		numSamples := endSample - startSample
		if numSamples <= 0 || ev.IsRest || len(ev.Pitches) == 0 {
			continue
		}

		inst := ev.Inst
		isDrum := IsPercussionInstrument(inst)

		gateRatio := ev.GateRatio
		if gateRatio <= 0 || gateRatio > 1.0 {
			gateRatio = 1.0
		}
		activeSamples := numSamples
		if gateRatio < 1.0 {
			activeSamples = int(math.Round(float64(numSamples) * gateRatio))
			if activeSamples < 1 {
				activeSamples = 1
			}
		}
		offSample := startSample + activeSamples - 1
		if offSample <= startSample {
			offSample = startSample + 1
		}
		if offSample > endSample-1 {
			offSample = endSample - 1
		}
		if offSample <= startSample {
			offSample = startSample + 1
		}

		const refVel uint8 = 104

		if isDrum {
			drumNote := uint8(ResolveGMDrumNote(inst))
			midiEvents = append(midiEvents,
				scheduledMIDIEvent{
					sampleOffset: startSample,
					order:        2,
					status:       0x90 | drumChannel,
					data1:        drumNote,
					data2:        refVel,
				},
				scheduledMIDIEvent{
					sampleOffset: offSample,
					order:        0,
					status:       0x80 | drumChannel,
					data1:        drumNote,
					data2:        0,
				},
			)
			continue
		}

		prog := ResolveGMProgram(inst)
		if ev.AttackScale > 0 && ev.AttackScale <= 0.20 && gateRatio <= 0.40 && (prog >= 40 && prog <= 43 || prog == 48 || prog == 49) {
			prog = 45 // Pizzicato Strings
		}
		if prog != lastProg {
			midiEvents = append(midiEvents, scheduledMIDIEvent{
				sampleOffset: startSample,
				order:        1,
				status:       0xC0 | melCh,
				data1:        uint8(prog & 0x7F),
				data2:        0,
			})
			if initialProg < 0 {
				initialProg = prog & 0x7F
			}
			lastProg = prog
		}

		// Map instrument vibrato depth to MIDI CC 1 (Modulation Wheel)
		modWheel := 0
		if inst.VibratoDepth > 0 {
			modWheel = int(math.Min(48.0, math.Round(inst.VibratoDepth*8.0)))
		}
		if modWheel != lastModWheel {
			midiEvents = append(midiEvents, scheduledMIDIEvent{
				sampleOffset: startSample,
				order:        1,
				status:       0xB0 | melCh,
				data1:        1,
				data2:        uint8(modWheel),
			})
			lastModWheel = modWheel
		}

		// Reset Pitch Bend to center (8192 = LSB 0, MSB 64) at start of note
		midiEvents = append(midiEvents, scheduledMIDIEvent{
			sampleOffset: startSample,
			order:        1,
			status:       0xE0 | melCh,
			data1:        0,
			data2:        64,
		})

		seenNotes := make(map[uint8]bool)
		for vIdx, sw := range ev.Pitches {
			if sw.StartFreq <= 0 {
				continue
			}
			midiNote := freqToClampedMIDINote(sw.StartFreq)
			if seenNotes[midiNote] {
				continue
			}
			seenNotes[midiNote] = true

			midiEvents = append(midiEvents,
				scheduledMIDIEvent{
					sampleOffset: startSample,
					order:        2,
					status:       0x90 | melCh,
					data1:        midiNote,
					data2:        refVel,
				},
				scheduledMIDIEvent{
					sampleOffset: offSample,
					order:        0,
					status:       0x80 | melCh,
					data1:        midiNote,
					data2:        0,
				},
			)

			if vIdx == 0 && sw.EndFreq > 0 && sw.StartFreq != sw.EndFreq && activeSamples > 441 {
				stepSamples := 441
				for s := stepSamples; s < activeSamples; s += stepSamples {
					p := float64(s) / float64(activeSamples)
					curFreq := sw.StartFreq * math.Pow(sw.EndFreq/sw.StartFreq, p)
					semiOffset := 12.0 * math.Log2(curFreq/sw.StartFreq)
					bendVal := int(math.Round(8192.0 + (semiOffset/2.0)*8191.0))
					if bendVal < 0 {
						bendVal = 0
					} else if bendVal > 16383 {
						bendVal = 16383
					}
					lsb := uint8(bendVal & 0x7F)
					msb := uint8((bendVal >> 7) & 0x7F)
					midiEvents = append(midiEvents, scheduledMIDIEvent{
						sampleOffset: startSample + s,
						order:        1,
						status:       0xE0 | melCh,
						data1:        lsb,
						data2:        msb,
					})
				}
			}
		}
	}

	sort.SliceStable(midiEvents, func(i, j int) bool {
		if midiEvents[i].sampleOffset != midiEvents[j].sampleOffset {
			return midiEvents[i].sampleOffset < midiEvents[j].sampleOffset
		}
		return midiEvents[i].order < midiEvents[j].order
	})

	const maxSliceFrames = 512
	var ctx C.AppleSynthContext
	cBankPath := C.CString(bankPath)
	defer C.free(unsafe.Pointer(cBankPath))

	appleAudioUnitInitMu.Lock()
	status := C.initAppleSynth(&ctx, cBankPath, C.double(SampleRate), C.UInt32(maxSliceFrames))
	appleAudioUnitInitMu.Unlock()
	if status != 0 {
		return nil, fmt.Errorf("initialize Apple CoreAudio MIDISynth/DLSSynth failed with OSStatus %d", int(status))
	}
	defer func() {
		appleAudioUnitInitMu.Lock()
		C.closeAppleSynth(&ctx)
		appleAudioUnitInitMu.Unlock()
	}()

	// Prime melodic channel 0 and drum channel 9 with clean studio settings
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|drumChannel), 7, 127, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|drumChannel), 10, 64, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|drumChannel), 11, 127, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|drumChannel), 91, 0, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|drumChannel), 93, 0, 0)

	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|melCh), 0, 0, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|melCh), 32, 0, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|melCh), 7, 127, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|melCh), 10, 64, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|melCh), 11, 127, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|melCh), 91, 0, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xB0|melCh), 93, 20, 0)
	C.sendMIDIEvent(&ctx, C.UInt32(0xE0|melCh), 0, 64, 0)
	if initialProg >= 0 {
		C.sendMIDIEvent(&ctx, C.UInt32(0xC0|melCh), C.UInt32(initialProg), 0, 0)
	}
	for i := 0; i < 4; i++ {
		if st := C.renderSlice(&ctx, C.UInt32(maxSliceFrames)); st != 0 {
			return nil, fmt.Errorf("Apple CoreAudio warm-up renderSlice failed with OSStatus %d", int(st))
		}
	}

	leftOut := make([]float32, totalSamples)
	rightOut := make([]float32, totalSamples)
	eventCursor := 0

	for samplePos := 0; samplePos < totalSamples; samplePos += maxSliceFrames {
		framesToRender := maxSliceFrames
		if samplePos+framesToRender > totalSamples {
			framesToRender = totalSamples - samplePos
		}
		sliceEnd := samplePos + framesToRender

		for eventCursor < len(midiEvents) && midiEvents[eventCursor].sampleOffset < sliceEnd {
			ev := midiEvents[eventCursor]
			relOffset := ev.sampleOffset - samplePos
			if relOffset < 0 {
				relOffset = 0
			}
			C.sendMIDIEvent(&ctx, C.UInt32(ev.status), C.UInt32(ev.data1), C.UInt32(ev.data2), C.UInt32(relOffset))
			eventCursor++
		}

		if st := C.renderSlice(&ctx, C.UInt32(framesToRender)); st != 0 {
			return nil, fmt.Errorf("Apple CoreAudio renderSlice at sample %d failed with OSStatus %d", samplePos, int(st))
		}

		leftSlice := unsafe.Slice((*float32)(unsafe.Pointer(ctx.leftBuf)), framesToRender)
		rightSlice := unsafe.Slice((*float32)(unsafe.Pointer(ctx.rightBuf)), framesToRender)
		copy(leftOut[samplePos:sliceEnd], leftSlice)
		copy(rightOut[samplePos:sliceEnd], rightSlice)
	}

	// Compute a single static track-level calibration scalar so that different gs_instruments.dls
	// patches match the DSL score's reference mixer fader level without per-note gain pumping.
	var auSumSq float64
	var activeCount int
	cursorSec = 0.0
	for _, ev := range tr.Events {
		if ev.DurationSec <= 0 {
			continue
		}
		startSample := int(math.Round(cursorSec * SampleRate))
		cursorSec += ev.DurationSec
		endSample := int(math.Round(cursorSec * SampleRate))
		if endSample > totalSamples {
			endSample = totalSamples
		}
		if ev.IsRest || len(ev.Pitches) == 0 || endSample <= startSample {
			continue
		}
		for i := startSample; i < endSample; i++ {
			l := float64(leftOut[i])
			r := float64(rightOut[i])
			e := 0.5 * (l*l + r*r)
			if e > 1e-8 {
				auSumSq += e
				activeCount++
			}
		}
	}
	trackScale := 1.0
	if activeCount > 0 {
		auRMS := math.Sqrt(auSumSq / float64(activeCount))
		if auRMS > 1e-4 {
			trackScale = 0.82 / auRMS
			if trackScale < 0.25 {
				trackScale = 0.25
			} else if trackScale > 6.5 {
				trackScale = 6.5
			}
		}
	}

	// Apply the score's continuous dynamic arrangement (inst.Volume, @vol curves, articulation gate, and stereo pan)
	// directly to the stereo AudioUnit stream without spectral cloning or chiptune LPF muffling.
	buf := make([]byte, (totalSamples*BytesPerFrame)&^3)
	cursorSec = 0.0

	for _, ev := range tr.Events {
		if ev.DurationSec <= 0 {
			continue
		}
		startSample := int(math.Round(cursorSec * SampleRate))
		cursorSec += ev.DurationSec
		endSample := int(math.Round(cursorSec * SampleRate))
		if endSample > totalSamples {
			endSample = totalSamples
		}
		numSamples := endSample - startSample
		if numSamples <= 0 || ev.IsRest || len(ev.Pitches) == 0 {
			continue
		}

		shapeAppleNoteEventStereo(
			buf[startSample*BytesPerFrame:endSample*BytesPerFrame],
			numSamples,
			leftOut[startSample:endSample],
			rightOut[startSample:endSample],
			ev,
			trackScale,
		)
	}

	return buf[:len(buf)&^3], nil
}

func shapeAppleNoteEventStereo(out []byte, numSamples int, auLeft, auRight []float32, ev NoteEvent, trackScale float64) {
	inst := ev.Inst
	if inst.Muted {
		return
	}
	durSec := float64(numSamples) / SampleRate
	isDrum := IsPercussionInstrument(inst)

	gateRatio := ev.GateRatio
	if gateRatio <= 0 || gateRatio > 1.0 {
		gateRatio = 1.0
	}
	activeSamples := numSamples
	if gateRatio < 1.0 {
		activeSamples = int(math.Round(float64(numSamples) * gateRatio))
		if activeSamples < 1 {
			activeSamples = 1
		}
	}
	activeDurSec := float64(activeSamples) / SampleRate

	attack := inst.Attack
	if ev.AttackScale > 0 {
		attack *= ev.AttackScale
	}

	panStart := inst.Pan
	panEnd := inst.Pan
	if ev.HasCustomPan {
		panStart = ev.PanStart
		panEnd = ev.PanEnd
	}
	panStart = math.Max(-1.0, math.Min(1.0, panStart))
	panEnd = math.Max(-1.0, math.Min(1.0, panEnd))
	staticPan := panStart == panEnd
	leftPan := math.Cos((panStart + 1.0) * math.Pi / 4.0)
	rightPan := math.Sin((panStart + 1.0) * math.Pi / 4.0)

	vol := inst.Volume
	if vol <= 0 {
		vol = 0.2
	}
	gainStart := 1.0
	gainMid := 1.0
	gainEnd := 1.0
	if ev.HasCustomGain {
		gainStart = ev.GainStart
		gainMid = ev.GainMid
		gainEnd = ev.GainEnd
	}

	for i := 0; i < activeSamples; i++ {
		t := float64(i) / SampleRate
		progress := t / durSec

		// Real percussion samples in gs_instruments.dls already have natural acoustic decay;
		// only apply the synthetic ADSR envelope to melodic/harmonic instruments.
		env := 1.0
		if !isDrum {
			env = getEnvelope(t, activeDurSec, attack, inst.Decay, inst.Sustain, inst.Release)
		}
		eventGain := evalGainCurve(progress, gainStart, gainMid, gainEnd, ev.HasGainMid)
		gain := trackScale * env * vol * eventGain

		if !staticPan {
			curPan := panStart + (panEnd-panStart)*progress
			leftPan = math.Cos((curPan + 1.0) * math.Pi / 4.0)
			rightPan = math.Sin((curPan + 1.0) * math.Pi / 4.0)
		}

		// Preserve stereo spread from CoreAudio while positioning around the target pan
		lSample := float64(auLeft[i]) * gain * leftPan * 1.4142
		rSample := float64(auRight[i]) * gain * rightPan * 1.4142

		leftVal := int16(math.Max(-1.0, math.Min(1.0, lSample)) * 32760)
		rightVal := int16(math.Max(-1.0, math.Min(1.0, rSample)) * 32760)
		idx := i * BytesPerFrame
		out[idx] = byte(leftVal)
		out[idx+1] = byte(leftVal >> 8)
		out[idx+2] = byte(rightVal)
		out[idx+3] = byte(rightVal >> 8)
	}
}

func freqToClampedMIDINote(freq float64) uint8 {
	n := int(math.Round(69.0 + 12.0*math.Log2(freq/440.0)))
	if n < 0 {
		return 0
	}
	if n > 127 {
		return 127
	}
	return uint8(n)
}

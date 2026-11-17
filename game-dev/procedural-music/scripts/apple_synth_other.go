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

//go:build !darwin

package main

import (
	"fmt"
	"runtime"
)

// SynthesizeScoreApple fails fast on non-macOS platforms because Apple CoreAudio / AudioToolbox
// DLS/SoundFont synthesis requires darwin frameworks.
func SynthesizeScoreApple(score *Score) ([]byte, error) {
	return nil, fmt.Errorf("apple high-fidelity synthesis requires macOS (CoreAudio / AudioToolbox), but current platform is %s/%s", runtime.GOOS, runtime.GOARCH)
}

func SynthesizeScoreAppleWithStems(score *Score) ([]byte, [][]byte, error) {
	return nil, nil, fmt.Errorf("apple high-fidelity synthesis requires macOS (CoreAudio / AudioToolbox), but current platform is %s/%s", runtime.GOOS, runtime.GOARCH)
}

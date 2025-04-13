rockyco: C simulation failed, solve this issue 'Size mismatch! Result: 0, Reference: 1
Test FAILED: Output does not match reference.
@E Simulation failed: Function 'main' returns nonzero value '1'.
ERROR: [SIM 211-100] 'csim_design' failed: nonzero return value.'

GitHub Copilot: I'll analyze the issue where the simulation found 0 peaks when the reference expects 1 peak.

Looking at the code, I've identified a logic error in the peak detection criteria. The issue is in the comparison that determines if a candidate should be added to the peak locations.

## Step-by-step solution:

1. The current code incorrectly compares `maxCheckCount` to `windowLength`. This doesn't make sense because:
   - `maxCheckCount` counts how many sequences have a local maximum at the candidate location
   - `windowLength` is just the size of the window being checked

2. The correct comparison should be between `maxCheckCount` and `validSeqCount` to verify that the candidate is a maximum in the window for ALL sequences that exceeded the threshold.

### [peakPicker.cpp](file:///home/jielei/Projects/UTS/peakPicker/HLS/origin/peakPicker.cpp)

Fix the comparison condition that determines if a candidate point is a peak.

````cpp
                WINDOW_CHECK:
                for (int w = 0; w < windowLength; w++) {
                    #pragma HLS PIPELINE II=1
                    if (xcorr[candidateLocation][seq] < xcorr[index + w][seq]) {
                        isMax = false;
                        break;
                    }
                }
                
                if (isMax) {
                    maxCheckCount++;
                }
            }
            
            // If candidate is maximum in window for all valid sequences, add to peak locations
            if (maxCheckCount == validSeqCount) {
                locations[numLocations] = candidateLocation;
                numLocations++;
                
                // Prevent buffer overflow
                if (numLocations >= MAX_LOCATIONS) {
                    break;
                }
            }
        }
    }
}
````

The key change is replacing `if (maxCheckCount == windowLength)` with `if (maxCheckCount == validSeqCount)`, which correctly checks if the candidate point is a maximum for all sequences that exceeded the threshold.


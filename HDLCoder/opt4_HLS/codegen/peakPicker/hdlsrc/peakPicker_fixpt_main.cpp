#include "peakPicker_fixptClass.hpp"
#include "peakPicker_fixptClass_tb.hpp"

int main()
{
  peakPicker_fixptClass_tb tb;
  input_struct inputs;
  output_struct outputs;
  while (!tb.is_stimuli_done()) {
    tb.generate_stimulus(inputs);
    peakPicker_fixpt_wrapper(inputs.xcorr, inputs.threshold, outputs.locations,
      outputs.valid);
    tb.check_output(outputs);
  }

  tb.print_pass_fail();
  if (tb.is_sim_passing()) {
    return 0;
  } else {
    return 1;
  }
}

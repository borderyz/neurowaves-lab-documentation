

function endExperiment(logFile, DEMO, expTable, trig, stim_fn, answer1, abortFlag)

    fprintf(logFile, 'N/A\tN/A\tEnd Experiment\t%f\tN/A\tN/A\tExperiment has ended\n', GetSecs());

    % Prepare data structure
    EXP.DEMO = DEMO;
    EXP.data = expTable;
    EXP.trig = trig;
    EXP.stim = stim_fn;
    EXP.aborted = abortFlag;  % true if aborted, false if finished normally

    % Save with a filename that indicates the experiment outcome
    if abortFlag
        save(['Sub-' answer1{1} '-vcp_aborted.mat'], 'EXP');
    else
        save(['Sub-' answer1{1} '-vcp.mat'], 'EXP');
    end

end

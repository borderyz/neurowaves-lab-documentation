

function endExperiment(logFile, DEMO, expTable, trig, stim_fn, answer1, abortFlag)

fprintf(logFile, '%s\t%s\t%s\t%.6f\t%s\t%s\t%s\n', ...
    'N/A', 'N/A', 'End Experiment', GetSecs(), 'N/A', 'N/A', 'Experiment has ended');

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

    fclose(logFile);
    
end

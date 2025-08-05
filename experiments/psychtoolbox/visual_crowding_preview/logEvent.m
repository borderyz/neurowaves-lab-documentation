function logEvent(logFile, trialNum, channel, phase, imageName, conditionLabel, message)
    if isnumeric(trialNum)
        trialStr = num2str(trialNum);
    else
        trialStr = trialNum;
    end
    if isnumeric(channel)
        channelStr = num2str(channel);
    else
        channelStr = channel;
    end
    fprintf(logFile, '%s\t%s\t%s\t%.6f\t%s\t%s\t%s\n', ...
        trialStr, channelStr, phase, GetSecs(), imageName, conditionLabel, message);
end

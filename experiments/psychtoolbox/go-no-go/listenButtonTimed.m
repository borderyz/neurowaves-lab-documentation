function [resp, time] = listenButtonTimed(offset, respTime)
    startTime = GetSecs;  % Record the starting time
    resp = [];            % Initialize response as empty (indicating no response)
    time = NaN;           % Initialize the response time as NaN

    while true
        % Check if the elapsed time has exceeded the maximum wait time
        if (GetSecs - startTime) > respTime
            % Optional: Display a timeout message
            disp('Response timed out.');
            break;  % Exit the loop if timed out
        end

        Datapixx('RegWrRd');
        kbcheck = dec2bin(Datapixx('GetDinValues'));

        % Check if the specific button is pressed based on offset
        if kbcheck(end-offset) == '1'
            for i_but = 1:9
                buttonBox(i_but) = str2num(kbcheck(end-9+i_but));
            end

            resp = find(buttonBox);
            time = GetSecs;  % Record the time of response

            % Only exit if exactly one response is detected
            if length(resp) == 1
                break;
            end
        end
    end
end
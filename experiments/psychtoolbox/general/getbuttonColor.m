function [box, color] = getbuttonColor(selection, blocking)
%GETBUTTONCOLOR Read Datapixx DINs and map to (box, color) like the Python version.
%   [box, color] = getbuttonColor()
%   [box, color] = getbuttonColor(selection)
%   [box, color] = getbuttonColor(selection, blocking)
%
% selection (optional): struct with fields:
%   - right_box: cellstr of colors to listen to, e.g. {'green','blue','yellow','red','white'}
%   - left_box : cellstr of colors to listen to
% blocking (optional, default true): if false, returns '' when no unique press.

    if nargin < 1 || isempty(selection)
        selection = struct();
    end
    if nargin < 2 || isempty(blocking)
        blocking = true;
    end

    % ---- Button mapping (match your Python dictionary) ----
    % response codes are 1..10 (we only use 1..10 range from the last 10 DIN bits)
    % Right box
    %   white:  response=6,  listen_to=5
    %   red:    response=10, listen_to=1
    %   yellow: response=9,  listen_to=2
    %   green:  response=8,  listen_to=3
    %   blue:   response=7,  listen_to=4
    % Left box
    %   white:  response=1,  listen_to=10
    %   red:    response=5,  listen_to=6
    %   yellow: response=4,  listen_to=7
    %   green:  response=3,  listen_to=8
    %   blue:   response=2,  listen_to=9

    % Build a response->(box,color) multimap (as cell arrays).
    % Each index i corresponds to response code i.
    RESP_TO_PAIRS = cell(1, 10);
    RESP_TO_PAIRS{6}  = [RESP_TO_PAIRS{6};  {"right box","white"}];
    RESP_TO_PAIRS{10} = [RESP_TO_PAIRS{10}; {"right box","red"}];
    RESP_TO_PAIRS{9}  = [RESP_TO_PAIRS{9};  {"right box","yellow"}];
    RESP_TO_PAIRS{8}  = [RESP_TO_PAIRS{8};  {"right box","green"}];
    RESP_TO_PAIRS{7}  = [RESP_TO_PAIRS{7};  {"right box","blue"}];

    RESP_TO_PAIRS{1}  = [RESP_TO_PAIRS{1};  {"left box","white"}];
    RESP_TO_PAIRS{5}  = [RESP_TO_PAIRS{5};  {"left box","red"}];
    RESP_TO_PAIRS{4}  = [RESP_TO_PAIRS{4};  {"left box","yellow"}];
    RESP_TO_PAIRS{3}  = [RESP_TO_PAIRS{3};  {"left box","green"}];
    RESP_TO_PAIRS{2}  = [RESP_TO_PAIRS{2};  {"left box","blue"}];

    ALL_RESPONSE_CODES = find(~cellfun(@isempty, RESP_TO_PAIRS));  %#ok<NASGU> % (not used elsewhere, kept for parity)

    % Normalize selection to a list of (box,color) pairs to allow
    % filtering pressed buttons.
    listenPairs = normalizeSelection(selection);

    % Main polling
    if blocking
        while true
            [respCodes, ok] = readActiveResponseCodes();
            if ~ok
                continue; % 0 or >1 high, keep polling
            end

            % Resolve candidates from resp code
            candidates = RESP_TO_PAIRS{respCodes(1)};
            candidates = filterBySelection(candidates, listenPairs);

            if size(candidates,1) == 1
                box   = candidates{1,1};
                color = candidates{1,2};
                return;
            elseif size(candidates,1) > 1
                warning('Ambiguous press: multiple (box,color) share this hardware line: %s', ...
                    strjoin(strcat(candidates(:,1), "/", candidates(:,2))', ', '));
                % keep polling until unambiguous
            end
        end
    else
        % Non-blocking: one-shot read; return '' if not uniquely resolvable
        [respCodes, ok] = readActiveResponseCodes();
        if ~ok
            box = ''; color = '';
            return;
        end
        candidates = RESP_TO_PAIRS{respCodes(1)};
        candidates = filterBySelection(candidates, listenPairs);

        if size(candidates,1) == 1
            box   = candidates{1,1};
            color = candidates{1,2};
        else
            if size(candidates,1) > 1
               pairs    = strcat(candidates(:,1), {'/'}, candidates(:,2));
               pairsStr = strjoin(pairs, ', ');
               warning('Ambiguous press: multiple (box,color) share this hardware line: %s', pairsStr);
            end
            box = ''; color = '';
        end
    end
end

% ---------- Helpers ----------

function pairs = normalizeSelection(selection)
% Convert selection struct into a unique list of {box,color} rows.
% selection.right_box = {'green','blue',...}
% selection.left_box  = {...}
    pairs = {};
    if isfield(selection, 'right_box') && ~isempty(selection.right_box)
        cols = lowerCellstr(selection.right_box);
        for i = 1:numel(cols)
            pairs(end+1, :) = {'right box', cols{i}}; %#ok<AGROW>
        end
    end
    if isfield(selection, 'left_box') && ~isempty(selection.left_box)
        cols = lowerCellstr(selection.left_box);
        for i = 1:numel(cols)
            pairs(end+1, :) = {'left box', cols{i}}; %#ok<AGROW>
        end
    end
    % deduplicate rows while preserving order
    if ~isempty(pairs)
        [~, ia] = unique(cellfun(@(a,b) [a '|' b], pairs(:,1), pairs(:,2), 'uni', 0), 'stable');
        pairs = pairs(ia, :);
    end
end

function out = lowerCellstr(in)
    if ischar(in), in = {in}; end
    out = in;
    for i = 1:numel(out)
        out{i} = lower(strtrim(out{i}));
    end
end

function filtered = filterBySelection(candidates, listenPairs)
    if isempty(listenPairs)
        filtered = candidates;
        return;
    end
    if isempty(candidates)
        filtered = candidates;
        return;
    end
    mask = false(size(candidates,1),1);
    for r = 1:size(candidates,1)
        for s = 1:size(listenPairs,1)
            if strcmp(candidates{r,1}, listenPairs{s,1}) && strcmp(candidates{r,2}, listenPairs{s,2})
                mask(r) = true; break;
            end
        end
    end
    filtered = candidates(mask, :);
end

function [respCodes, singleHigh] = readActiveResponseCodes()
% Reads Datapixx DIN, returns response codes 1..10 that are high,
% and a flag that is true only if exactly one valid response line is high.
    Datapixx('RegWrRd');
    rawVal  = Datapixx('GetDinValues');
    bitsStr = dec2bin(rawVal);

    % Keep only the last 10 bits (rightmost). If shorter, pad on the left.
    if numel(bitsStr) < 10
        bitsStr = [repmat('0', 1, 10 - numel(bitsStr)) bitsStr];
    else
        bitsStr = bitsStr(end-9:end);
    end

    % Map to codes: position i => response code i (1..10), like the Python version.
    respCodes = find(bitsStr == '1');

    % Only accept if exactly one code is high
    singleHigh = (numel(respCodes) == 1);
end

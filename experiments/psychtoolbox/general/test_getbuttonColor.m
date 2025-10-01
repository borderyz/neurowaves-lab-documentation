% Block until any mapped button is pressed:
pair = getbuttonColor()

% Non-blocking poll:
pair = getbuttonColor([], false);
if isempty(pair), disp('nothing yet'); end

% Listen only to a subset:
sel = struct();
sel.('right box') = {'blue'};
sel.('left box')  = {'white','red'};
pair = getbuttonColor(sel);

% 1) Listen to all buttons, blocking:

Datapixx('Open');

[box,color] = getbuttonColor();

% 2) Listen to a subset, blocking:
sel.right_box = {'green','blue','yellow'};
sel.left_box  = {'white','red'};
[box,color] = getbuttonColor(sel, true);

% 3) Non-blocking poll:
[box,color] = getbuttonColor(struct(), false);
if isempty(box)
    disp('No unique press yet.');
end


Datapixx('Close');
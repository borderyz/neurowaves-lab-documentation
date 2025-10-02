Datapixx('Open');

Datapixx('DisablePixelMode');
Datapixx('RegWr');


sel = struct('right box', {{'blue'}}, 'left box',  {{'white','red'}});
%sel.('right box') = {'blue'};
%sel.('left box')  = {'white','red'};


while true
    % Block until any mapped button is pressed:
    pair = getButtonColor(sel)
    
    disp(['button pressed', pair]);
    WaitSecs(0.5)
end




% % Non-blocking poll:
% pair = getbuttonColor([], false);
% if isempty(pair), disp('nothing yet'); end
% 
% % Listen only to a subset:
% sel = struct();
% sel.('right box') = {'blue'};
% sel.('left box')  = {'white','red'};
% pair = getbuttonColor(sel);

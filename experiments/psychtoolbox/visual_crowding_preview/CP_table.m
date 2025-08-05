% % Define conditions and image indices
% side = [-1 1];
% preview = [0 1];
% questionType = [0 1];
% crowding = [1 2];
% connection = [0 1 ];
% imageIndex = 1:13;

% Define conditions and image indices
% side = [-1 1];
% preview = [0 1];
questionType = [0 1];
% crowding = [1 2 3];
crowding = [1 2 3 4];
connection = [1 2 3 4];
imageIndex = 1:20;

% Calculate the total number of images
numConnections = length(connection);
numCrowding = length(crowding);
numImagesPerCondition = length(imageIndex);
totalImages = numConnections * numCrowding * numImagesPerCondition; % This should be 300

% n_flipped = floor(totalImages/2);         % 149
% n_normal  = totalImages - n_flipped;        % 150
% previewValues = [zeros(n_flipped, 1); ones(n_normal, 1)];
% % Randomly shuffle the preview values
% previewValues = previewValues(randperm(totalImages));

n_negative = floor(totalImages/2);
n_positive = totalImages - n_negative;
balancedSides = [-1 * ones(n_negative, 1); 1 * ones(n_positive, 1)]; % -1 is left; 1 is right
balancedSides = balancedSides(randperm(totalImages)); % Shuffle the sides randomly



% Check if the total number of images matches your expectation
% assert(totalImages == 300, 'Total number of images does not match 300.');

% Initialize the table
expTable = [];
i_trial = 1;

% Loop through each combination of connection, crowding, and imageIndex
for i_connection = 1:length(connection)
    for i_crowding = 1:length(crowding)
        for i_imageIndex = 1:length(imageIndex)
            % Randomly select conditions for side, preview, and questionType
            selectedSide = balancedSides(i_trial);
%             selectedPreview = previewValues(i_trial);
            selectedQuestionType = questionType(randi(length(questionType)));
            
            % Populate the table with the selected and looped conditions
%             expTable(i_trial, :) = [selectedSide, selectedPreview, selectedQuestionType, crowding(i_crowding), connection(i_connection), imageIndex(i_imageIndex)];
            expTable(i_trial, :) = [selectedSide, selectedQuestionType, crowding(i_crowding), connection(i_connection), imageIndex(i_imageIndex)];

            i_trial = i_trial + 1;
        end
    end
end

% Labels for the table
% expLabels = {'side', 'preview', 'questionType', 'crowding', 'connection', 'imageIndex'};
expLabels = {'side', 'questionType', 'crowding', 'connection', 'imageIndex'};

% Convert to table and randomize
expTable = array2table(expTable, 'VariableNames', expLabels);
expTable = expTable(randperm(size(expTable, 1)), :);

% Display the size of the table
% disp(['Table size: ', num2str(size(expTable, 1)), ' rows']);

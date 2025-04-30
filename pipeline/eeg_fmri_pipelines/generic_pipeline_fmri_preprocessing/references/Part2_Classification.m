%% fMRI Classification Tutorial
% This tutorial demonstrates how to analyze fMRI data using classification techniques
% It shows how patterns of brain activity can be used to distinguish between different experimental conditions

%% Overview
% This tutorial walks through the process of analyzing fMRI data using classification techniques.
% We'll start with simulated data and gradually build up to more complex analyses.
%
%% 1. Introduction
% fMRI data measures brain activity across many small brain regions (voxels)
% We'll see how to use patterns of activity to tell different experimental conditions apart
%
% Instead of looking at each voxel separately, we'll combine them to get better results
% This tutorial will show:
% 1. Why single voxels aren't great at telling conditions apart
% 2. How combining voxels improves classification
% 3. How to check if our results are meaningful

%% 2. Setting Up the Simulation
% Clear any existing variables and figures
clear all
close all

% Set parameters for our simulated data:
numVoxels = 50;        % Number of voxels we're measuring
expDuration = 8;       % Number of times we repeat the experiment (runs)
numConditions = 3;     % Number of different experimental conditions
meanResponse = 1;      % Average response level
noiseLevel = 0.5;      % Amount of random variation in the measurements

%% 3. Generating Simulated Data
% 3.1 Create Basic Activity Patterns
% Create the basic activity patterns for each condition
% Each condition gets its own unique pattern across voxels
conditionPatterns = meanResponse + rand(numVoxels,numConditions) -0.5;

% 3.2 Add Noise to Simulate Real Data
% Add noise to make it more realistic
% Data is organized as: runs × voxels × conditions
datafMRI = zeros(expDuration,numVoxels,numConditions);
for runIdx = 1:expDuration
    datafMRI(runIdx,:,:) = conditionPatterns + randn(numVoxels,numConditions)*noiseLevel;
end

%% 4. Visualizing the Data
% 4.1 Activity Patterns Across All Conditions
% Show the activity patterns for all conditions
% Each subplot shows one condition's pattern across voxels and runs
figure(1); clf;  % Create a new figure and clear any existing plots
for condIdx = 1:numConditions
    subplot(1, numConditions, condIdx);  % Make a subplot for each condition
    imagesc(datafMRI(:,:,condIdx),[min(datafMRI(:)) max(datafMRI(:))]);  % Show the activity pattern
    xlabel('Voxel');  % Label the x-axis
    ylabel('Run');    % Label the y-axis
    title(sprintf('Condition %d', condIdx));  % Title for this subplot
    colormap(gray);   % Use grayscale colors
    colorbar;         % Show the color scale
end

% 4.2 Average Activity Across Conditions
% Show average activity across all voxels
% This helps us see if conditions are different on average
figure(2); clf;
meanResponses = squeeze(mean(mean(datafMRI,1),2));  % Calculate mean for each condition
responseVariability = squeeze(std(mean(datafMRI,2)));  % Calculate how much responses vary
bar(meanResponses); hold on;  % Make a bar plot of the means
h = errorbar(1:numConditions,meanResponses,2*responseVariability,2*responseVariability,'k');  % Add error bars
set(h,'LineStyle','none');  % Make error bars solid
ylim([0 max(meanResponses)*1.2]);  % Set y-axis limits
xlabel('Condition');  % Label x-axis
ylabel('Average Response');  % Label y-axis
box off;  % Remove the box around the plot
xlim([0 numConditions+1]);  % Set x-axis limits

%% 5. Analyzing Single Voxel Responses
% 5.1 Response Distribution for a Single Voxel
% Look at how responses vary for a single voxel
% This helps us see if we can tell conditions apart using just one voxel
binWidth = 10;  % How many bins to use in the histogram

whichVoxel = 1;  % Which voxel to look at (try changing this number)

figure(3); clf;  % Create a new figure
val = datafMRI(:,whichVoxel,:);  % Get all responses for this voxel
val = val(:);  % Flatten into a single list
minValue = min(val);  % Find the smallest response
maxValue = max(val);  % Find the largest response
binEdges = linspace(minValue,maxValue,binWidth);  % Create evenly spaced bins

% Plot histogram for each condition
for condIdx = 1:numConditions
    histCondition = hist(datafMRI(:,whichVoxel,condIdx),binEdges);  % Count responses in each bin
    plot(binEdges,histCondition/sum(histCondition*1/binWidth),'LineWidth',2);  % Plot the histogram
    hold on;  % Keep the plot for adding more lines
end
hold off;  % Stop adding to the plot
xlabel(sprintf('Voxel %g response',whichVoxel));  % Label x-axis
ylabel('Probability');  % Label y-axis
box off;  % Remove the box around the plot
title(sprintf('Response Distribution for Voxel %g',whichVoxel));  % Add title
legend(arrayfun(@(x) sprintf('Condition %d', x), 1:numConditions, 'UniformOutput', false));  % Add legend

% 5.2 Fitting Normal Distributions
% Fit normal distributions to the response patterns
% This helps us understand how well we can tell conditions apart
numBinsForFit = 100;  % How many points to use for the fitted curve

whichVoxel = 2;  % Which voxel to look at (try changing this number)

figure(4); clf;  % Create a new figure
val = datafMRI(:,whichVoxel,:);  % Get all responses for this voxel
val = val(:);  % Flatten into a single list
minValue = min(val);  % Find the smallest response
maxValue = max(val);  % Find the largest response
xValues = linspace(minValue,maxValue,numBinsForFit);  % Create evenly spaced x-values

% Calculate and plot the fitted curves for each condition
for condIdx = 1:numConditions
    meanCondition = mean(datafMRI(1:expDuration-1,whichVoxel,condIdx));  % Calculate mean response
    stdCondition = std(datafMRI(1:expDuration-1,whichVoxel,condIdx));  % Calculate standard deviation
    fittedCondition = normpdf(xValues,meanCondition,stdCondition);  % Calculate the normal distribution
    
    plot(xValues,fittedCondition/sum(fittedCondition*1/numBinsForFit),'LineWidth',2);  % Plot the fitted curve
    hold on;  % Keep the plot for adding more lines
end
hold off;  % Stop adding to the plot
box off;  % Remove the box around the plot
title(sprintf('Fitted Distributions for Voxel %g',whichVoxel));  % Add title
xlabel('Response');  % Label x-axis
ylabel('Probability');  % Label y-axis
legend(arrayfun(@(x) sprintf('Condition %d', x), 1:numConditions, 'UniformOutput', false));  % Add legend

%% 6. Classification Analysis 
% 6.1 Single Voxel Classification
% Now we'll implement a simple classifier to distinguish between conditions
% using a single voxel's response pattern. We'll use a probabilistic approach
% where we estimate the likelihood of observing a particular response given
% each condition. 
% 1. Model each condition's response distribution (using mean and standard deviation)
% 2. For a new test response, calculate which condition's distribution it most likely belongs to
% 3. Assign the test response to the condition with highest probability

whichVoxel = 1; % try change this number to look at different voxels

% Use leave-one-run-out cross-validation to test classification accuracy
correctClassifications = 0;
totalTests = 0;

for testRun = 1:expDuration
    % Use all other runs for training
    trainingRuns = setdiff(1:expDuration, testRun);
    
    % Calculate mean and std for each condition using training data
    trainMeans = zeros(1, numConditions);
    trainStds = zeros(1, numConditions);
    for condIdx = 1:numConditions
        trainMeans(condIdx) = mean(datafMRI(trainingRuns, whichVoxel, condIdx)); % Calculate mean response for each condition
        trainStds(condIdx) = std(datafMRI(trainingRuns, whichVoxel, condIdx)); % Calculate standard deviation for each condition
    end
    
    % Test on left-out run
    for condIdx = 1:numConditions
        testResponse = datafMRI(testRun, whichVoxel, condIdx); % Get the response for the left-out run
        
        % Calculate probability under each condition's distribution
        probs = zeros(1, numConditions);
        for c = 1:numConditions
            probs(c) = normpdf(testResponse, trainMeans(c), trainStds(c)); % Calculate probability of test response under each condition's distribution
        end
        
        % Classify based on highest probability
        [~, predictedCond] = max(probs); % Assign the test response to the condition with highest probability
        
        % Check if classification was correct
        if predictedCond == condIdx % If the predicted condition matches the true condition
            correctClassifications = correctClassifications + 1;  % Increment the number of correct classifications
        end
        totalTests = totalTests + 1; % Increment the total number of tests
    end
end

% Calculate and report classification accuracy
accuracy = correctClassifications / totalTests; % Calculate the accuracy
fprintf('Voxel %i classification accuracy: %.2f%%\n', whichVoxel, accuracy * 100); % Print the accuracy

%% 7. Multi-Voxel Analysis

%%
% Now let's try adding a second voxel

whichVoxel1 = 1; % index of first voxel
whichVoxel2 = 2;  % index of second voxel
colors = {'b', 'r', 'g'}; % color for three conditions

figure(1); clf;
% Plot all three conditions as scatter plot for two voxels
for condIdx = 1:numConditions
    scatter(datafMRI(:,whichVoxel1,condIdx), datafMRI(:,whichVoxel2,condIdx), 50, colors{condIdx}, 'filled');
    hold on;
end
hold off;

% Add labels and title
xlabel(sprintf('Voxel %d Response', whichVoxel1));
ylabel(sprintf('Voxel %d Response', whichVoxel2));
title('Response Patterns Across Two Voxels');
legend('Condition 1', 'Condition 2', 'Condition 3');
box off;
grid on;

%%
% Now let's try adding a third voxel

whichVoxel1 = 1; % index of first voxel
whichVoxel2 = 2; % index of second voxel
whichVoxel3 = 3; % index of third voxel

figure(1); clf;
% Plot all three conditions as 3D scatter plot
for condIdx = 1:numConditions
    scatter3(datafMRI(:,whichVoxel1,condIdx), datafMRI(:,whichVoxel2,condIdx), ...
        datafMRI(:,whichVoxel3,condIdx), 80, colors{condIdx}, 'filled');
    hold on;
end
hold off;

% Add labels and title
xlabel(sprintf('Voxel %d Response', whichVoxel1));
ylabel(sprintf('Voxel %d Response', whichVoxel2));
zlabel(sprintf('Voxel %d Response', whichVoxel3));
title('Response Patterns Across Three Voxels');
legend('Condition 1', 'Condition 2', 'Condition 3');
box off;

%%

voxelPairs = [1 2; 1 3; 2 3];
conditionPairs = [1 2; 1 3; 2 3];

figure(1); clf;

% Create 3x3 subplot layout
for row = 1:3  % For each voxel pair
    voxel1 = voxelPairs(row,1);
    voxel2 = voxelPairs(row,2);
    
    for col = 1:3  % For each condition pair
        cond1 = conditionPairs(col,1);
        cond2 = conditionPairs(col,2);
        
        subplot(3,3,(row-1)*3 + col);
        
        % Plot scatter for first condition
        scatter(datafMRI(:,voxel1,cond1), datafMRI(:,voxel2,cond1), colors{cond1}, 'filled');
        hold on;
        % Plot scatter for second condition
        scatter(datafMRI(:,voxel1,cond2), datafMRI(:,voxel2,cond2), colors{cond2}, 'filled');
        hold off;
        
        % Set consistent axis limits across all subplots
        xlim([min(datafMRI(:)) max(datafMRI(:))]);
        ylim([min(datafMRI(:)) max(datafMRI(:))]);
        
        % Add labels and title
        xlabel(sprintf('Voxel %g', voxel1));
        ylabel(sprintf('Voxel %g', voxel2));
        title(sprintf('Cond %g vs %g', cond1, cond2));
        box off;
        
        % Add legend
        legend(sprintf('Cond %g', cond1), sprintf('Cond %g', cond2));
    end
end


%%
% Now perform classification using all voxels together
% Create labels for each condition and run
conditionLabels = repmat(1:numConditions,[expDuration 1]);

% Split data into training and testing sets
numFolds = 5;         % Number of cross-validation folds
cv = cvpartition(1:expDuration,'Kfold',numFolds);

% Initialize confusion matrix to store results
confusionMatrix = zeros(numConditions,numConditions,cv.NumTestSets);

% Perform cross-validated classification
for foldIdx = 1:cv.NumTestSets
    % Get indices for training and testing
    trainIdx = cv.training(foldIdx);
    testIdx = cv.test(foldIdx);
    
    % Reshape data for classification
    trainData = reshape(datafMRI(trainIdx,:,:),[cv.TrainSize(foldIdx)*numConditions numVoxels]);
    testData = reshape(datafMRI(testIdx,:,:),[cv.TestSize(foldIdx)*numConditions numVoxels]);
    trainLabels = reshape(conditionLabels(trainIdx,:),[cv.TrainSize(foldIdx)*numConditions 1]);
    testLabels = reshape(conditionLabels(testIdx,:),[cv.TestSize(foldIdx)*numConditions 1]);
    
    % Perform classification
    predictedLabels = classify(testData,trainData,trainLabels,'diagLinear');
    
    % Store results in confusion matrix
    for trueCondition = 1:numConditions
        for predictedCondition = 1:numConditions
            confusionMatrix(trueCondition,predictedCondition,foldIdx) = ...
                sum(testLabels==trueCondition & predictedLabels==predictedCondition);
        end
    end
end

% Calculate average confusion matrix and accuracy
confusionMatrix = sum(confusionMatrix,3)/sum(cv.TestSize);
accuracy = mean(diag(confusionMatrix));

% Plot confusion matrix
figure(1); clf;
imagesc(confusionMatrix,[0 1]);
title(sprintf('Classification Accuracy: %.2f',accuracy));
xlabel('Presented Condition');
ylabel('Predicted Condition');
colorbar;

%%
% Analyze how classification performance changes with number of voxels
% This helps understand how many voxels are needed for good classification

numBootstrap = 10;    % Number of bootstrap samples, adjust this number and see how the figure changes

bootstrapAccuracy = zeros(numVoxels,numBootstrap);
for bootstrapIdx = 1:numBootstrap
    for numVoxelsUsed = 1:numVoxels
        % Randomly select voxels
        randomVoxels = randperm(numVoxels);
        randomVoxels = randomVoxels(1:numVoxelsUsed);
        
        % Perform classification
        [~, bootstrapAccuracy(numVoxelsUsed,bootstrapIdx)] = ...
            crossValClassify(datafMRI(:,randomVoxels,:),conditionLabels,numFolds);
    end
end

% Plot results
figure(1); clf;
plot(1:numVoxels,prctile(bootstrapAccuracy,50,2),'k','LineWidth',4); hold on;

% Can you add the 95% confidence interval around the mean in this plot?









hold on;
set(h,'Color','k');
set(h,'LineStyle',':');
hold off;

ylim([0 1.1]);
xlim([0 numVoxels]);
xlabel('Number of Voxels');
ylabel('Classification Accuracy');
box off;
title('Classification Performance vs. Number of Voxels');


%% What is our chance distribution?

% Test if classification performance is significantly above chance
% We do this by randomly permuting the condition labels

% Can you try to implement this?









%% What happens when we change the Signal to Noise ratio of the data?

% Can you try to make a figure of classification accuracy as a function of
% SNR?











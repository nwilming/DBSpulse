function randmat = generate_random (numsubjects)
% function generate_random (numsubjects)
%
% this function generates a matlab structure containing random orders of
% stimulus presentation for NUMSUBJECTS subjects.  the structure is 2
% dimensional: subjects x trials [img]
%
% all parameters (number of trials per block, number of blocks, etc.) are
% defined within the code and can be changed if needed.
%
% original author: cquigley@uos.de, 2006
% simplified by jss for demo purposes

if nargin < 1  % Need Parameter: Number of Subjects
    help generate_random
    return
end

% PARAMETERS TO CHANGE DEPENDING ON YOUR EXPERIMENT:

% list of image indices. maybe also be sth simple like (1:20) 
images = [1 2 3 4 5 31 32 33 101 102 103 104];
% END PARAMETERS

numimages = length(images);

% INITIALISE THE STRUCTURE
% main experiment randmat is 2 dimensional: subjects x trials
randmat = struct('image', NaN);

for subject = 1 : numsubjects

    shuffled = randperm(numimages); 

    for trial = 1 : length(images)
        randmat(subject, trial).image = int16( images( shuffled( trial ) ) );
    end

end

end

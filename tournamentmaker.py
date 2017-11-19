# -*- coding: utf-8 -*-
"""
Created on 2015-12-08
Version Date: 2017-11-10

@author: Matthew Woelfle
Contact Info: mdwoelfle@gmail.com
"""

# Loads participant list from ${workDir/}participants.txt
# Creates one round each time run, building off prior rounds

from random import uniform
# try:
import cPickle as pickle
# except:
#    import pickle
import os
import numpy as np
import warnings  # Allow throwing of warnings

# %%

# !!HARD KLUDGE RIGHT HERE!!
# to avoid:
# PicklingError: Can't pickle __main__.playercard: it's not the same object
#   as __main__.playercard
if 'players' not in locals():
    class playercard(object):
        """
        Define class to track each player
        """

        # Initialize the class
        def __init__(self,
                     name,
                     idNum,
                     nbyes=None,
                     opponents=None,
                     partners=None,
                     roundScores=None,
                     score=None,
                     tables=None,
                     ):
            # Name the player
            self.name = name
            # Give the player an id number
            self.id = idNum
            # Set player's total number of byes as int
            if nbyes is None:
                self.nbyes = 0
            else:
                self.nbyes = nbyes
            # Set player's opponents for each round as list of opponent lists
            if opponents is None:
                self.opponents = []
            else:
                self.opponents = opponents
            # Set player's partner for each round as list
            if partners is None:
                self.partners = []
            else:
                self.partners = partners
            # Set player's scores for each round as list
            if roundScores is None:
                self.roundScores = []
            else:
                self.roundScores = roundScores
            # Set player's total score as int
            if score is None:
                self.score = sum(self.roundScores)
            else:
                self.score = score
            # Set table player sat at for each round
            if tables is None:
                self.tables = []
            else:
                self.tables = tables

        # Set thing that will show up when class is called.
        #   Should be super detailed
        def __repr__(self):
            # Thing to return
            s = ('playercard(\'{:s}\', {:d}, '.format(self.name,
                                                      self.id) +
                 'nbyes={:d}, '.format(self.nbyes) +
                 'opponents=[[\'' +
                 '\'], [\''.join(['\', \''.join([k
                                                 if k else 'None'
                                                 for k in j])
                                  for j in self.opponents]) +
                 '\']], ' +
                 'partners=[\'' +
                 '\', \''.join([j if j else 'None'
                                for j in self.partners]) +
                 '\'], ' +
                 'roundScores=[' +
                 ', '.join(['{:d}'.format(j) for j in self.roundScores]) +
                 '], ' +
                 'score={:d}, '.format(self.score) +
                 'tables=[' + ', '.join(['{:d}'.format(j) if j else 'None'
                                         for j in self.tables]) + ']' +
                 ')'
                 )

            # Return the thing.
            return s

        # Set other thing which should be simpler.
        def __str__(self):
            # Return simple thing
            s = ('Player card for {:s}'.format(self.name))

            # Return the thing.
            return s

        def addscore(self,
                     roundScore,
                     jRd=None):
            """
            Add score for the given (current) round and update total
            """
            if jRd is None:
                jRd = len(self.roundScores) + 1
                print('Adding score for {:s} for round {:d}'.format(
                      self.name, jRd))

            # Add score for round to playercard
            try:
                # Try to add score for previous round
                self.roundScores[jRd-1] = roundScore
            except IndexError:
                # Otherwise, add score for next round
                if len(self.roundScores) == (jRd - 1):
                    self.roundScores.append(roundScore)
                else:
                    raise IndexError('Round number too high; missing scores.')

            # Update total score
            self.score = sum(self.roundScores)

        def printallrounds(self):
            """
            Print round info for all logged rounds
            """
            for jRd in range(len(self.tables)):
                self.printround(jRd+1)

        def printround(self,
                       jRd,
                       ):
            """
            Print info for a given round for this player
            """
            # Create header for round print out
            s = '\n---Round {:d} for {:s}---\n'.format(jRd, self.name)

            # Add details for round print out
            if self.tables[jRd-1] is None:
                s = s + 'Bye Round'
            else:
                s = (s +
                     '      Table: {:d}\n'.format(self.tables[jRd-1]) +
                     '    Partner: {:s}\n'.format(self.partners[jRd-1]) +
                     '  Opponents: {:s}, {:s}\n'.format(
                         self.opponents[jRd-1][0],
                         self.opponents[jRd-1][1])
                     )
                # Attempt to get score for round
                try:
                    s = (s +
                         'Round Score: {:d}'.format(self.roundScores[jRd-1])
                         )
                except IndexError:
                    s = (s + 'Round Score: Unreported')

            # Print round information for given round
            print s


def addopponents(playerDict,
                 newRoundList,
                 newByeList):
    """
    Add opponents to player cards
    """

    # Loop and add partners by table
    for jT in range(0, len(newRoundList), 4):
        # Add opponents for first person at table
        try:
            playerDict[newRoundList[jT]].opponents.append(
                [newRoundList[jT+2], newRoundList[jT+3]])
        except KeyError as ke:
            if 'Filler' in newRoundList[jT]:
                continue
            else:
                raise KeyError(ke)

        # Add opponents for second person at table
        try:
            playerDict[newRoundList[jT+1]].opponents.append(
                [newRoundList[jT+2], newRoundList[jT+3]])
        except KeyError as ke:
            if 'Filler' in newRoundList[jT+1]:
                continue
            else:
                raise KeyError(ke)

        # Add opponents for third person at table
        try:
            playerDict[newRoundList[jT+2]].opponents.append(
                [newRoundList[jT], newRoundList[jT+1]])
        except KeyError as ke:
            if 'Filler' in newRoundList[jT+2]:
                continue
            else:
                raise KeyError(ke)

        # Add opponents for fourth person at table
        try:
            playerDict[newRoundList[jT+3]].opponents.append(
                [newRoundList[jT], newRoundList[jT+1]])
        except KeyError:
            if 'Filler' in newRoundList[jT+3]:
                continue
            else:
                raise KeyError(ke)

    # Assign opponents for players with byes
    for jP in newByeList:
        playerDict[jP].opponents.append([None, None])

    # Return updated playerDict
    return playerDict


def addpartners(playerDict,
                newRoundList,
                newByeList):
    """
    Add partners to player cards
    """
    # Add partners to player cards
    # Every 2 people in the list are partners (0 with 1, 2 with 3, etc.), so
    #   only need every other index in loop. Assigns parterns of x to x+1 and
    #   vice versa each loop iteration
    for jP in range(0, len(newRoundList), 2):
        # Add following player to current index's partner list
        try:
            playerDict[newRoundList[jP]].partners.append(
                newRoundList[jP+1])
        except KeyError as ke:
            if 'Filler' in newRoundList[jP]:
                continue
            else:
                raise KeyError(ke)

        # Add current player to following index's partner list
        try:
            playerDict[newRoundList[jP + 1]].partners.append(
                newRoundList[jP])
        except KeyError as ke:
            if 'Filler' in newRoundList[jP+1]:
                continue
            else:
                raise KeyError(ke)

    # Assign partners for players with byes
    for jP in newByeList:
        playerDict[jP].partners.append(None)

    # Return updated playerDict
    return playerDict


def addscores(playerDict,
              playerName,
              selfScore,
              opponentScore,
              jRd=None):
    """
    Add scores for a given round to playercards

    Here jRd is actual round number with 1 being first index
    """
    # Assume most recent round if not provided
    if jRd is None:
        print('Assuming score is for latest round (Round {:d})'.format(
              len(playerDict[playerName].tables)))
        jRd = len(playerDict[playerName].tables)

    # Ensure round has been run before assigning scores
    if jRd > len(playerDict[playerName].tables):
        raise IndexError('Round {:d} not yet reached; '.format(jRd) +
                         'cannot add score for this round.')

    # Add score for given player
    playerDict[playerName].addscore(selfScore, jRd)

    # Add score for player's partner
    playerDict[playerDict[playerName].partners[jRd-1]].addscore(
        selfScore, jRd)

    # Add score for player's opponents
    playerDict[playerDict[playerName].opponents[jRd-1][0]].addscore(
        opponentScore, jRd)
    playerDict[playerDict[playerName].opponents[jRd-1][1]].addscore(
        opponentScore, jRd)


def addtables(playerDict,
              newRoundList,
              newByeList):
    """
    Add tables to player cards
    """
    # Loop and add tables by table
    #   This time increment by 0:1:nTables rather than 0:4:nPlayersInRound
    for jT in range(0, len(newRoundList)/4):
        for jS in range(4):
            # Add opponents for jS person at table (jT + 1 to fix indexing)
            try:
                playerDict[newRoundList[4*jT+jS]].tables.append(jT+1)
            except KeyError as ke:
                if 'Filler' in newRoundList[4*jT+jS]:
                    continue
                else:
                    raise KeyError(ke)

    # Assign tables for players with byes
    for jP in newByeList:
        playerDict[jP].tables.append(None)

    # Return updated playerDict
    return playerDict


def assignbyes(playerDict,
               finalRd_flag=False):
    """
    Create list of players who will be forced to have byes this round

    Returns:
        list of players who will be assigned a bye this round
    """
    # Make list of current bye counts
    nbyeList = np.array([playerDict[jp].nbyes for jp in playerDict.keys()])

    # Determine minimum number of byes any player has had
    minByes = nbyeList.min()

    # Sanity check to ensure byes stay balanced
    if not any([nbyeList.min() == nbyeList.max(),
                nbyeList.min() == nbyeList.max() - 1]):
        raise ValueError('Byes are unbalanced')

    # Determine number of byes needed to yield full tables
    nByesNeeded = np.mod(len(playerDict), 4)

    if finalRd_flag:
        # On final round, assign byes to all players who have not yet had the
        #   maximum number of byes
        newByeList = [playerName
                      for playerName in playerDict.keys()
                      if playerDict[playerName].nbyes == minByes]
        if len(newByeList) == len(playerDict):
            warnings.warn('Byes are currently even. Creating final round ' +
                          'with all players. Using this round may result ' +
                          'in uneven byes.')
        else:
            return newByeList

    # Select players who will have a bye this round
    newByeList = [playerName
                  for playerName in playerDict.keys()
                  if playerDict[playerName].nbyes == minByes
                  ][:nByesNeeded]
    # Select extra players to have another bye if needed to get to number of
    #   required byes
    if len(newByeList) < nByesNeeded:
        nByesStillNeeded = nByesNeeded - len(newByeList)
        newByeList.append(
            [playerName
             for playerName in playerDict.keys()
             if playerDict[playerName].nbyes != minByes
             ][:nByesStillNeeded]
            )

    return newByeList


def backupround(players,
                workDir,
                roundNum,
                scores=False):
    """
    Create back up file of end of round state in case need to back up/reset
    """

    # Save state in case recovery necessary (backup)
    if not scores:
        rdStateFile = ('{:s}holdstate_startrd{:d}.txt'.format(
            workDir, roundNum))
    else:
        rdStateFile = ('{:s}holdstate_endrd{:d}_withScores.txt'.format(
            workDir, roundNum))

    # try:
    # Don't write over previous score including file
    if os.path.isfile(rdStateFile) and scores:
        print('Skipping initial score-including backup as file already ' +
              'exists ({:s})'.format(rdStateFile))
    else:
        with open(rdStateFile, "wb") as output:
            pickle.dump((players, roundNum), output, pickle.HIGHEST_PROTOCOL)
    # except:
    #     print("could not save state.")

    # Attempt to save master state file (always most recent state)
    stateFile = (workDir + 'holdstate.txt')
    if os.path.isfile(stateFile):
        os.remove(stateFile)
    try:
        with open(stateFile, "wb") as output:
            pickle.dump((players, roundNum), output, pickle.HIGHEST_PROTOCOL)
    except:
        print('could not save state')


def createround(playerDict, jRd,
                backupRd_flag=True,
                finalRd_flag=False,
                forceScoreReporting_flag=True,
                maxRdAttempts=1e6,
                opponentRepeatRdLimit=1,
                pinnedPlayer_flag=False,
                pinnedPlayer=None,
                pinnedTable=1,
                verbose_flag=False,
                workDir=None,
                writeScoreboard_flag=True):
    """
    Create new tournament round
    """

    # Ensure have all scores from previous round before generating a new round
    if forceScoreReporting_flag and (jRd > 1):
        missingTables, missingPlayers = findmissingscores(
            playerDict,
            jRd=jRd-1,
            return_flag=True,
            verbose_flag=False)
        if len(missingTables) != 0:
            s = printmissingscores(playerDict,
                                   jRd-1,
                                   missingTables,
                                   missingPlayers,
                                   returnAsString_flag=True)
            raise RuntimeError('Must report all scores before creating ' +
                               'new round.\n' + s)

    # Create backup of round with scores prior to creating new round
    if backupRd_flag and (jRd > 1):
        backupround(playerDict,
                    workDir,
                    jRd-1,
                    scores=True)

    # Write out current scoreboard to file
    if writeScoreboard_flag and (jRd > 1):
        printscoreboard(playerDict,
                        standingsFile=(
                            workDir +
                            'scoreboard_endRd{:d}.txt'.format(jRd-1)),
                        toWhere='file',
                        )

    # Make list of current bye counts
    nbyeList = np.array([playerDict[jp].nbyes for jp in playerDict.keys()])

    # Determine minimum number of byes any player has had
    minByes = nbyeList.min()

    # Select players who will have a bye this round
    #   For finalRd_flag == True, assigns byes to all players who have not
    #   yet experienced the maximum number of byes
    newByeList = assignbyes(playerDict,
                            finalRd_flag=finalRd_flag)

    # Create list of eligible players for this round
    #   i.e. those not in newByeList
    eligiblePlayers = {playerDict[jp].name: playerDict[jp]
                       for jp in playerDict.keys()
                       if jp not in newByeList}

    # Create dummy players for final round if needed to round out tables
    if np.mod(len(eligiblePlayers), 4) != 0:
        if finalRd_flag:
            # Add dummy players to the player pool to round out the final
            #   round
            for j in range(4 - np.mod(len(eligiblePlayers), 4)):
                eligiblePlayers['Filler{:d}'.format(j)] = playercard(
                    'Filler{:d}'.format(j),
                    -j,
                    nbyes=eligiblePlayers[eligiblePlayers.keys()[0]].nbyes)
        else:
            raise RuntimeError('Something went wrong...')

    # True if round will have no repeat partners or <opponents>.
    #   Initialize as False to force while loop to initialize.
    validRound = False
    # Keep track of guess number
    nGuess = 0

    # Create new round without repeating partners or <opponents>
    while not validRound:
        if verbose_flag:
            print('----ATTEMPTING TO CREATE ROUND----')

        # Assign each eligible player a random postion in the list of players
        orderer = [uniform(0, 1) for x in range(len(eligiblePlayers))]

        # Sort players by randomly assigned positions from orderer
        newRoundList = [
            x for (y, x) in sorted(zip(orderer, eligiblePlayers.keys()))]
        if verbose_flag:
            print('NewRoundList:')
            print(newRoundList)

        # Check if the current proposed round is valid
        validRound = isroundvalid(eligiblePlayers,
                                  newRoundList,
                                  minByes=minByes,
                                  opponentRepeatRdLimit=opponentRepeatRdLimit,
                                  verbose_flag=verbose_flag
                                  )

        # Increment guess tracker and give up if necessary
        nGuess = nGuess + 1
        if nGuess > maxRdAttempts:
            warnings.warn('No good round found. Giving up. Will use latest '
                          'round found as next round. All rounds after ' +
                          'this point may be suspect.')
            break

    # Ensure pinned player never moves tables (if requested)
    if pinnedPlayer_flag:
        newRoundList = pinplayertotable(newRoundList,
                                        pinnedPlayer,
                                        pinnedTable)

    # Add tables to player cards
    playerDict = addtables(playerDict,
                           newRoundList,
                           newByeList)

    # Add partners to player cards
    playerDict = addpartners(playerDict,
                             newRoundList,
                             newByeList)

    # Add opponents to player cards
    playerDict = addopponents(playerDict,
                              newRoundList,
                              newByeList)

    # Increment bye count for players with byes and assign score of 0
    for playerName in newByeList:
        playerDict[playerName].nbyes = playerDict[playerName].nbyes + 1
        playerDict[playerName].addscore(0, jRd=jRd)

    # Write human readable round assignments to files
    writeround(newRoundList,
               newByeList,
               jRd,
               filename=workDir + 'round' + str(jRd) + '.txt',
               workDir=workDir)

    # Create backup of end of round state
    if backupRd_flag:
        backupround(playerDict,
                    workDir,
                    jRd,
                    scores=False)

    return (playerDict, newRoundList)


def findmissingscores(playerDict,
                      jRd=None,
                      return_flag=False,
                      verbose_flag=True):
    """
    Find tables who have not yet reported a score for a given round
    """
    if jRd is None:
        print('Assuming looking at latest round (Round {:d})'.format(
              len(playerDict[playerDict.keys()[0]].tables)))
        jRd = len(playerDict[playerDict.keys()[0]].tables)

    # Ensure round has been run before searching for missing scores
    if jRd > len(playerDict[playerDict.keys()[0]].tables):
        raise IndexError('Round {:d} not yet reached; '.format(jRd) +
                         'cannot search for missing scores for this round.')

    # Create lists to hold missing players and missing tables
    missingPlayers = []
    missingTables = []

    # Loop through players and see who has not reported a score
    for jP in playerDict.keys():
        try:
            playerDict[jP].roundScores[jRd-1]
        except IndexError:
            missingPlayers.append(jP)
            if playerDict[jP].tables[jRd-1] not in missingTables:
                missingTables.append(playerDict[jP].tables[jRd-1])

    # Print out missing players and tables
    if verbose_flag:
        printmissingscores(playerDict,
                           jRd,
                           missingTables,
                           missingPlayers)

    if return_flag:
        return (missingTables, missingPlayers)


def getstandings(playerDict):
    """
    Create list of standings by player score
    """
    # Get list of players
    playerList = playerDict.keys()

    # Get list of total score
    scoreList = [playerDict[jP].score for jP in playerList]

    # Sort by total score
    rankedList = [x for (y, x) in sorted(zip(scoreList, playerList))][::-1]

    # Return result
    return rankedList


def isroundvalid(playerDict,
                 newRoundList,
                 minByes=None,
                 opponentRepeatRdLimit=1,
                 verbose_flag=False,
                 ):
    """
    Check if the current new round is a valid one

    Returns:
        True if proposed round is valid.
    """

    # Check if repeat partners are present; return False if yes
    if repeatpartners(playerDict,
                      newRoundList,
                      verbose_flag=verbose_flag):
        if verbose_flag:
            print('Repeat partners found, retrying...')
        return False

    # Check if played against same opponents in previous round
    if repeatopponents(playerDict,
                       newRoundList,
                       roundLimit=opponentRepeatRdLimit,
                       verbose_flag=verbose_flag):
        if verbose_flag:
            print('Repeated opponents from ' +
                  'previous {:0d} '.format(opponentRepeatRdLimit) +
                  'round(s) found, retrying...')
        return False

    # If all criteria met, return True for "yes, this is a valid round"
    return True


def loadplayers(stateFile,
                workDir,
                participantFile=None):
    """
    Load players in tournament from file
    """
    try:
        with open(stateFile, "rb") as inputFile:
            (players, roundNum) = pickle.load(inputFile)
            roundNum = roundNum + 1
    except IOError:
        # Set participant list location if none provided
        if participantFile is None:
            participantFile = (workDir + 'participants.txt')

        # Open text file with participants
        text_file = open(participantFile)

        # Read in names from participant list
        try:
            names = text_file.readlines()
        finally:
            text_file.close()
        names = [names[jName][:-1]
                 if names[jName][-1] == "\n" else names[jName]
                 for jName in range(len(names))]

        # Create player card for each player
        players = {names[jName]: playercard(names[jName], jName)
                   for jName in range(len(names))}
        roundNum = 1

    return (players, roundNum)


def pinplayertotable(newRoundList,
                     pinnedPlayer,
                     pinnedTable=1):
    """
    Ensure one player doesn't have to move
    """
    # Only execute if pinned player does not have a bye
    if pinnedPlayer in newRoundList:
        # Get index of player who needs to stay put
        oldIndex = newRoundList.index(pinnedPlayer)

        # Find first index of that player's table
        oldTableStartIndex = oldIndex - np.mod(oldIndex, 4)

        # Pull player names of people at that table
        fixedTableList = newRoundList[oldTableStartIndex:
                                      oldTableStartIndex + 4]

        # Move people from the table to which pinnedPlayer is pinned
        newRoundList[oldTableStartIndex:oldTableStartIndex+4] = (
            newRoundList[4*(pinnedTable - 1):4*(pinnedTable - 1) + 4])

        # Move people to the pinnedTable
        newRoundList[4*(pinnedTable - 1):4*(pinnedTable - 1) + 4] = (
            fixedTableList)

    # Return amended newRoundList
    return newRoundList


def printmissingscores(playerDict,
                       jRd,
                       missingTables,
                       missingPlayers,
                       returnAsString_flag=False,
                       ):
    """
    Print nicely formatted list of tables and players for which scores are
        missing
    """
    # Set string based on whether scores are unreported
    if len(missingTables) == 0:
        # If not scores unreported, good to go.
        s = 'No missing scores for Round {:d}.'.format(jRd)
    else:
        # If scores are unreported, say that.
        s = 'Missing scores for Round {:d} from:'.format(jRd)
        # Loop through tables to create nicely formatted string for ouputting
        #   missing tables and players at those tables
        for jT in missingTables:
            s = (s + '\nTable {:d}: '.format(jT) +
                 ', '.join([jP for jP in missingPlayers
                            if (playerDict[jP].tables[jRd-1] == jT)])
                 )

    # Either return output as string (for exception use, mainly)
    #   or directly print string
    if returnAsString_flag:
        return s
    else:
        print(s)


def printscoreboard(playerDict,
                    standingsFile=None,
                    toWhere='cmd',
                    workDir=None,
                    ):
    """
    Print formatted list of standings
    """
    # Get list of player names sorted by points (highest first)
    rankedList = getstandings(playerDict)

    # Get minimum number of byes
    minByes = np.min(np.array([playerDict[jP].nbyes
                               for jP in playerDict.keys()]))

    # Get maximum number of rounds with scores reported
    maxRds = np.max(np.array([len(playerDict[jP].roundScores)
                              for jP in playerDict.keys()]))

    # If printing to commmand line:
    # if toWhere.lower() in ['cmd', 'screen']:
    # Set header row
    header = ('Standings after Round {:d}\n'.format(maxRds) +
              ' #  Name' + ' '*12 + 'Pts  Pts/Rd\n')
    # Get nicely formatted string for printing
    s = '\n'.join(['{:2d}  {:15s}{:4d}{:s} {:6.1f}'.format(
                   jS+1,
                   playerDict[jP].name +
                   ('*' if playerDict[jP].nbyes > minByes else ''),
                   playerDict[jP].score,
                   ('-' if len(playerDict[jP].roundScores) < maxRds
                    else ' '),
                   (playerDict[jP].score/float(
                       len(playerDict[jP].roundScores) -
                       playerDict[jP].nbyes)
                    if playerDict[jP].nbyes != len(playerDict[jP].roundScores)
                    else 0)
                   )
                   for jS, jP in enumerate(rankedList)])
    # Explain asterisks and dashes in footer row
    footer = ('\n* = player has had an extra bye' +
              '\n- = player has an unreported score')
    if toWhere.lower() in ['cmd', 'screen']:
        print(header + s + footer)
    elif toWhere.lower() in ['file', 'f']:
        if standingsFile is None:
            # Ensure workdir exists
            if workDir is None:
                workDir = os.getcwd() + os.sep

            # Set filename
            standingsFile = (workDir + 'scoreboard_rd{:d}.txt'.format(maxRds))

        # Remove old file if needed
        if os.path.isfile(standingsFile):
            os.remove(standingsFile)

        # Open file for writing
        f = open(standingsFile, 'w')

        # Write to file
        f.write(header + s + footer)

        # Close file
        f.close()


def repeatopponents(playerDict,
                    newRoundList,
                    roundLimit=1,
                    verbose_flag=False):
    """
    Check if opponents are repeated from the previous n rounds

    Returns if at least one player has the same opponent as they had in the
        previous n rounds.
    """

    # Initially assume partners are not repeated
    opponentCheck = False

    # Loop through and check opponents by table
    for jT in range(0, len(newRoundList), 4):
        # Check first person at table
        firstPriorOpponents = [
            player
            for sublist
            in playerDict[newRoundList[jT]].opponents[-roundLimit::]
            for player in sublist]
        if any([(newRoundList[jT+2] in firstPriorOpponents),
                (newRoundList[jT+3] in firstPriorOpponents),
                ]):
            if verbose_flag:
                print('{:s} has a repeat opponent'.format(
                      playerDict[newRoundList[jT]].name))
                print('Attempted opponents: {:s}, {:s}'.format(
                      newRoundList[jT+2], newRoundList[jT+3]))
                print('Previous opponents: ' +
                      ', '.join(firstPriorOpponents))
            opponentCheck = True

        # Check second person at table
        secondPriorOpponents = [
            player
            for sublist
            in playerDict[newRoundList[jT+1]].opponents[-roundLimit::]
            for player in sublist]
        if any([(newRoundList[jT+2] in secondPriorOpponents),
                (newRoundList[jT+3] in secondPriorOpponents),
                ]):
            if verbose_flag:
                print('{:s} has a repeat opponent'.format(
                      playerDict[newRoundList[jT+1]].name))
                print('Attempted opponents: {:s}, {:s}'.format(
                      newRoundList[jT+2], newRoundList[jT+3]))
                print('Previous opponents: ' +
                      ', '.join(secondPriorOpponents))
            opponentCheck = True

        # Exit loop if any opponentCheck is True
        if opponentCheck:
            return opponentCheck

    if verbose_flag:
        print('No repeat opponents found over past {:0d} rounds'.format(
              roundLimit))

    return opponentCheck


def repeatpartners(playerDict,
                   newRoundList,
                   verbose_flag=False):
    """
    Check if repeated partners will occur if the current order is used to
        assign tables.

    Returns:
        True if one or more partner pairs repeated

    Notes:
        May need to add option to allow for a finite number of times for
            repeating a partner pairing.
    """
    # Every 2 people are partners, so only need to check every other
    #   i.e. check if 1 is in 0's partner list, if 3 is in 2's, etc.
    #   and skip check if player name is None (empty seat)
    partnerCheck = [newRoundList[x+1] in playerDict[newRoundList[x]].partners
                    for x in np.arange(0, len(newRoundList), 2)
                    # if newList[x] is not None
                    ]
    if verbose_flag:
        print('PartnerCheck:')
        print(partnerCheck)

    # Return True if any partners match
    return any(partnerCheck)


def roundinfotostdout(players,
                      roundNum):
    """
    Print round information to stdout
    """

    a = [players[jp].nbyes for jp in players.keys()]
    print('End Rd: ' + str(roundNum))
    print('Min bye: ' + str(min(a)))
    print('Max bye: ' + str(max(a)))


def writeround(newRoundList,
               newByeList,
               jRd,
               filename=None,
               workDir=None):
    """
    Write table assignments to file
    """
    if filename is None:
        filename = (workDir + 'rounds.txt')
    f = open(filename, 'w')

    # Write round table by table to text file
    f.write('\n-------\nRound ' + str(jRd) + '\n-------\n')
    for jTable in range(len(newRoundList)/4):
        f.write('\nTable ' + str(jTable + 1) + '\n\n')
        f.write(str(newRoundList[4*jTable + 0]) + '\n')
        f.write(str(newRoundList[4*jTable + 1]) + '\n')
        f.write('-vs-\n')
        f.write(str(newRoundList[4*jTable + 2]) + '\n')
        f.write(str(newRoundList[4*jTable + 3]) + '\n')

    # Write bye list to end of text file
    f.write('\nByes:\n\n')
    for playerName in newByeList:
        f.write(str(playerName) + '\n')

    # Close file
    f.close()


# %% Main working section
if __name__ == '__main__':
    # %% Define flags and other run criteria

    # True to produce bye-balancing round
    finalRd_flag = True

    # Set number of rounds over which opponents will not be repeated
    opponentRepeatRdLimit = 2

    # Pin player to a table if needed
    pinnedPlayer_flag = True
    pinnedPlayer = 'Player01'
    pinnedTable = 1

    # Set maximum number of guesses for creating a round
    maxRdAttempts = 1e6

    # True to print out more comments and test statements
    verbose_flag = False

    # True to make backup of round file
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!! THIS SHOULD ALWAYS BE TRUE UNLESS YOU !!!
    # !!!   ARE REALLY SURE YOU DON'T NEED IT   !!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    backupRd_flag = True

    # Directory used for saving files
    workDir = r'C:\Users\woelfle\Documents\PersonalStuff\euchre\2017\\'

    # List of players to delete before running next round
    playersToDelete = [None]  # None  # list to remove players

    # Location to search for prior round state if not in memory
    loadFile = (workDir + 'holdstate.txt')
    # loadFile = (workDir + 'holdstate_endrd3_withScores.txt')

    # %% Do things

    # Load player list from file
    if 'players' not in locals():
        players, roundNum = loadplayers(loadFile,
                                        workDir)

    # Remove players as needed
    if playersToDelete is not None:
        for jPlayer in playersToDelete:
            players.pop(jPlayer, None)

    # Create list of players for each round
    if 'roundNum' not in locals():
        roundNum = 1
    (players, newRound) = createround(
        players,
        roundNum,
        finalRd_flag=finalRd_flag,
        forceScoreReporting_flag=True,
        maxRdAttempts=maxRdAttempts,
        opponentRepeatRdLimit=opponentRepeatRdLimit,
        pinnedPlayer_flag=pinnedPlayer_flag,
        pinnedPlayer=pinnedPlayer,
        pinnedTable=pinnedTable,
        verbose_flag=verbose_flag,
        workDir=workDir,
        )

    # Write out rounds info
    roundinfotostdout(players, roundNum)

    # increment round number
    roundNum = roundNum + 1

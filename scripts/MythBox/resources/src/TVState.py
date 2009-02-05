#
#  MythBox for XBMC - http://mythbox.googlecode.com
#  Copyright (C) 2009 analogue@yahoo.com
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

"""
File    : /mythtv/libs/libmythtv/tv.h
Object  : TVState - enumeration of the states used by TV and TVRec
Protocol: QUERY_REMOTEENCODER::GETSTATE

TODO: Move to constants module 
"""

#
# Error State, if we ever try to enter this state errored is set.
#
Error = -1                  

#
# None State, this is the initial state in both TV and TVRec, it
# indicates that we are ready to change to some other state.
#
OK = 0         

#
# Watching LiveTV is the state for when we are watching a
# recording and the user has control over the channel and
# the recorder to use. 
#
WatchingLiveTV = 1          

#
# Watching Pre-recorded is a TV only state for when we are
# watching a pre-existing recording.
#
WatchingPreRecorded = 2

#
# Watching Recording is the state for when we are watching
# an in progress recording, but the user does not have control
# over the channel and recorder to use.
#
WatchingRecording = 3

#
# Recording Only is a TVRec only state for when we are recording
# a program, but there is no one currently watching it.
#
RecordingOnly = 4

#
# This is a placeholder state which we never actualy enter,
# but is returned by GetState() when we are in the process
# of changing the state.
#
ChangingState = 5
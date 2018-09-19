#
# Copyright 2018 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


import sys
import json

def findNewPr(oldPrList, newPrList):

    foundNewPrId = ""

    # loop over the list
    for newItem in newPrList:
        if not newItem in oldPrList:
            # New item detected
            # We can only trigger one releaes at a time, so we
            # only want to return 1 (and do the rest on future iterations)
            # This will return the last one we found.
            foundNewPrId = ""

    return foundNewPrId

if server is None:
    print "No Bitbucket server provided."
    sys.exit(1)

request = HttpRequest(server, username, password)
context = "/rest/api/1.0/projects/%s/repos/%s" % (project, repository)
pr_path = "%s/%s?state=OPEN" % (context, "pullrequests")
response = request.get(pr_path, contentType = 'application/json')

if not response.isSuccessful():
    if response.status == 404 and triggerOnInitialPublish:
        print "Repository '%s' not found in bitbucket. Ignoring." % (repo_full_name)

        if not triggerState:
            triggerState = ''
    else:
        print "Failed to fetch branch information from Bitbucket server %s" % server['url']
        response.errorDump()
    sys.exit(1)
else:
    info = json.loads(response.response)

    # build a list of known pull requests
    # build a map of the commit ids for each branch
    current_knownPrList = []
    for prItem in info["values"]:
        prItemId = prItem["id"]
        current_knownPrList.append(str(prItemId))

    # trigger state is perisisted as json
    newTriggerState = json.dumps(current_knownPrList)

    # if anything has changed
    if triggerState != newTriggerState:
        if len(triggerState) == 0:
            prev_knownPrList = [] # Empty list
        else:
            prev_knownPrList = json.loads(triggerState) # Loads triggerState into a string list

    # Run findNewPr
    CheckPullRequest = findNewPr(prev_knownPrList, current_knownPrList)
    # If we find something new in the list
    if CheckPullRequest != "":
        # Fill in output variable
        pullRequestId = CheckPullRequest
        # Append it to our old list
        prev_knownPrList.append(CheckPullRequest)

        # We'll persist our updated list to the triggerState
        # We don't use the current_knownPrList, because it could have 2 or more
        # new pull requests, and saving current->old means we can only trigger once.
        triggerState = json.dumps(prev_knownPrList)

        print("Bitbucket triggered release for pull request: %s" % (pullRequestId))

    else:
        # Nothing new found
        # Shouldn't be necessary - persist it anyways?
        triggerState = json.dumps(current_knownPrList)

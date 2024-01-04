import os
import csv

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, voterlogin_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db_path = os.path.join(os.path.dirname(__file__), 'electionyoda.db')
db = SQL(f"sqlite:///{db_path}")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    electionmessage = ""
    voterlistmessage = ""

    username = db.execute("SELECT fname FROM Users WHERE id = ?", session["user_id"])

    # display a list of elections
    elections = db.execute("SELECT * FROM Elections WHERE user_id = ? ORDER BY status", session["user_id"])
    if len(elections) == 0:
        electionmessage = ("You have not created any elections.")

    # display a list of voterlists
    voterlists = db.execute("SELECT * FROM Voterlists WHERE user_id = ? ORDER BY uploaddate DESC, uploadtime DESC", session["user_id"])

    for voterlist in voterlists:
        with open(voterlist["filename"], mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            votercount = 0
            votercount = sum(1 for row in csv_reader)
        voterlist["votercount"] = votercount

    if len(voterlists) == 0:
        voterlistmessage = ("You have not created any voterlists.")

    return render_template("index.html", username = username[0]['fname'], elections = elections, voterlists = voterlists, voterlistmessage = voterlistmessage, electionmessage = electionmessage)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email address", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM Users WHERE email = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/voterlogin", methods=["GET", "POST"])
def voterlogin():
    """Log voter in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM Voters WHERE email = ?", request.form.get("email"))

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email address", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure username exists and password is correct
        elif len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Ensure password was submitted
        elif not request.form.get("electionid"):
            return apology("must provide the Election ID", 403)

        # Check for a valid election id
        rows = db.execute("SELECT * FROM Elections WHERE election_id = ?", request.form.get("electionid"))
        if len(rows) != 1:
            return apology("invalid Election ID", 403)
        else:
            election_status = db.execute("SELECT status FROM Elections WHERE election_id = ?", request.form.get("electionid"))
            if election_status[0]["status"] == 'Inactive':
                return apology("Election is currently inactive", 403)
            else:
                #check if voter is in the voter list
                voterlistname = db.execute("SELECT filename FROM Voterlists WHERE voterlist_id = (SELECT voterlist_id FROM Elections WHERE election_id = ?)", request.form.get("electionid"))
                with open(voterlistname[0]["filename"], mode='r') as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    line_count = 0
                    for row in csv_reader:
                        if line_count == 0:
                            line_count += 1
                        if row["Email Address"] == request.form.get("email"):

                            #check if the voter has already voted
                            voteremail = db.execute("SELECT * FROM Votes WHERE election_id = ? AND voter_emailaddress = ?", request.form.get("electionid"), request.form.get("email"))
                            if len(voteremail) == 1:
                                alert = "Alert!"
                                message = "You have already voted."
                                return render_template("votermessage.html", alert = alert, message = message)
                            else:

                                # Remember which user has logged in
                                session["email"] = row["Email Address"]

                                # Render the correct voting page
                                electionnamerow = db.execute ("SELECT name FROM Elections WHERE election_id =?", request.form.get("electionid"))
                                electionname = electionnamerow[0]["name"]
                                electionid = request.form.get("electionid")
                                username = row["Full Name"]

                                ballotquestionrow = db.execute ("SELECT ballot_id, question FROM Ballots WHERE election_id =?", request.form.get("electionid"))
                                ballotquestion = ballotquestionrow[0]["question"]

                                ballotid = ballotquestionrow[0]["ballot_id"]

                                option1row = db.execute ("SELECT option1 FROM Ballots WHERE election_id =?", request.form.get("electionid"))
                                option1 = option1row[0]["option1"]

                                option2row = db.execute ("SELECT option2 FROM Ballots WHERE election_id =?", request.form.get("electionid"))
                                option2 = option2row[0]["option2"]

                                option3row = db.execute ("SELECT option3 FROM Ballots WHERE election_id =?", request.form.get("electionid"))
                                option3 = option3row[0]["option3"]

                                return render_template ("vote.html", electionname = electionname,
                                                            electionid = electionid,
                                                            ballotid = ballotid,
                                                            username = username,
                                                            ballotquestion = ballotquestion,
                                                            option1 = option1,
                                                            option2 = option2,
                                                            option3 = option3)
                        else:
                            line_count += 1
                    return apology("Your name is not in the voter list", 403)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("voterlogin.html")

@app.route("/buildelection", methods=["GET", "POST"])
def buildelection():
    if request.method == "POST":

        #check if all fields have been submitted

        if not request.form.get("electiontitle"):
            return apology("must provide election title", 400)

        if not request.form.get("startdate"):
            return apology("must provide start date", 400)

        if not request.form.get("enddate"):
            return apology("must provide end date", 400)

        if not request.form.get("quorum"):
            return apology("must provide minimum voting %", 400)

        if not request.form.get("question"):
            return apology("must provide a ballot question", 400)

        if not request.form.get("option1"):
            return apology("must provide option 1", 400)

        if not request.form.get("option2"):
            return apology("must provide option 2", 400)

        if not request.form.get("option3"):
            return apology("must provide option 3", 400)

        if not request.form.get("voterlist"):
            return apology("must provide a voter list", 400)

        rows = db.execute("SELECT * FROM Elections WHERE name = ?", request.form.get("electiontitle"))
        if len(rows) != 0:
            return apology ("Election title already exists. Select a different title", 400)

        name = request.form.get("electiontitle")
        startdate = request.form.get("startdate")
        enddate = request.form.get("enddate")
        quorum = request.form.get("quorum")
        question = request.form.get("question")
        option1 = request.form.get("option1")
        option2 = request.form.get("option2")
        option3 = request.form.get("option3")
        voterlist_id = request.form.get("voterlist")

        db.execute("INSERT INTO Elections (name, startdate, enddate, quorum, user_id, status, voterlist_id) VALUES (?, ?, ?, ?, ?, ?, ?)", name, startdate, enddate, quorum, session["user_id"], "Inactive", voterlist_id)

        election_dict = db.execute("SELECT election_id FROM Elections WHERE name = ?", name)
        election_ids = election_dict[0]["election_id"]

        db.execute("INSERT INTO Ballots (question, option1, option2, option3, election_id) VALUES (?, ?, ?, ?, ?)", question, option1, option2, option3, election_ids)

        success = ("Election: " + name + " was successfully created.")

        return render_template("success.html", message = success)

    else:
        voterlists = db.execute("SELECT voterlist_id, voterlistname FROM Voterlists WHERE user_id = ?", session["user_id"])

        return render_template("buildelection.html", voterlists = voterlists)

@app.route("/voterlist_upload", methods=["GET", "POST"])
def voterlist_upload():
    if request.method == "POST":
        voterlistname = request.form.get("voterlistname")

        file = request.files['voterlistfile']

        if file:
            # Generate a timestamp using the current date and time
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            uploaddate = datetime.now().strftime("%d/%m/%Y")
            uploadtime = datetime.now().strftime("%H:%M:%S")
            dbfilename = file.filename
            # Concatenate the timestamp with the original filename
            filename = os.path.join("uploads", f"{timestamp}_{file.filename}")

            # Save the file with the new filename
            file.save(filename)

            #Insert voter list file details into SQL db.
            db.execute ("INSERT INTO Voterlists (voterlistname, filename, dbfilename, uploaddate, uploadtime, user_id) VALUES (?, ?, ?, ?, ?, ?)", voterlistname, filename, dbfilename, uploaddate, uploadtime, session["user_id"])

            success = (voterlistname + " was successfully created on " + uploaddate + " at " + uploadtime)
            return render_template("success.html", message = success)


    return render_template("voterlist_upload.html")

@app.route("/electionhome", methods=["GET", "POST"])
@login_required
def electionhome():
   # Get the election id from the dashboard table. Figure out how to get a "form.request.get from a text instead of a form input
   # using that id, pull out each detail of the election from the db
   # populate the html page based on the above details.

    if request.method == "POST":

        election_id = request.form.get("hiddenElectionId")
        election = db.execute ("SELECT * FROM Elections WHERE election_id = ?", election_id)
        name = election[0]["name"]
        status = election[0]["status"]

        # Count the no. of voters in the voterlist
        voterlistname = db.execute("SELECT filename FROM Voterlists WHERE voterlist_id = (SELECT voterlist_id FROM Elections WHERE election_id = ?)", election_id)
        if voterlistname:
            with open(voterlistname[0]["filename"], mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                votercount = 0
                for row in csv_reader:
                    votercount += 1
        else:
            return redirect("/")

        # Count the no. of votes casted
        votescastedrow = db.execute("SELECT COUNT(*) FROM Votes WHERE election_id = ?", election_id)
        votescasted = votescastedrow[0]["COUNT(*)"]

        quorum = election[0]["quorum"]
        votingpercent = (round(votescasted / votercount * 100, 2))
        startdate = election[0]["startdate"]
        enddate = election[0]["enddate"]
        todaytimestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        ballotquestionrow = db.execute("SELECT question FROM Ballots WHERE election_id = ?", election_id)
        ballotquestion = ballotquestionrow[0]["question"]

        options = db.execute ("SELECT option1, option2, option3 FROM Ballots WHERE election_id = ?", election_id)
        option1 = options[0]["option1"]
        option2 = options[0]["option2"]
        option3 = options[0]["option3"]

        votes = db.execute("SELECT vote, COUNT(*) AS count FROM Votes WHERE election_id = ? GROUP BY vote", election_id)

        # Initializing the dictionary
        votes1 = votes2 = votes3 = 0

        # Processing vote counts
        for row in votes:
            vote_option = row["vote"]
            count = row["count"]

            if vote_option == "1":
                votes1 = count
            elif vote_option == "2":
                votes2 = count
            elif vote_option == "3":
                votes3 = count

        if votes1:
            vote1percent = round(votes1 / votescasted * 100, 2)
        else:
            vote1percent = "-"

        if votes2:
            vote2percent = round(votes2 / votescasted * 100, 2)
        else:
            vote2percent = "-"

        if votes3:
            vote3percent = round(votes3 / votescasted * 100, 2)
        else:
            vote3percent = "-"

        return render_template ("electionhome.html", name = name,
                                election_id = election_id,
                                status = status,
                                votercount = votercount,
                                votescasted = votescasted,
                                quorum = quorum,
                                votingpercent = votingpercent,
                                startdate = startdate,
                                enddate = enddate,
                                todaytimestamp = todaytimestamp,
                                ballotquestion = ballotquestion,
                                option1 = option1,
                                option2 = option2,
                                option3 = option3,
                                votes1 = votes1,
                                votes2 = votes2,
                                votes3 = votes3,
                                vote1percent = vote1percent,
                                vote2percent = vote2percent,
                                vote3percent = vote3percent)

    return render_template("electionhome.html")

@app.route("/vote", methods=["GET", "POST"])
@voterlogin_required
def vote():
    if request.method == "POST":
        if not request.form.get("ballot1"):
            return apology("you must select an option", 400)
        else:
            vote = request.form.get("ballot1")
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            voter_emailaddress = session["email"]
            election_id = request.form.get('hiddenElectionId')
            ballot_id = request.form.get('hiddenBallotId')

            #Update Votes db with the new vote
            db.execute("INSERT INTO Votes (voter_emailaddress, election_id, ballot_id, vote, votingdate) VALUES (?, ?, ?, ?, ?)", voter_emailaddress, election_id, ballot_id, vote, timestamp)
            alert = ("Thank you!")
            message = ("Your vote from email address " + voter_emailaddress + " was successfully registered on " + timestamp + ".")
            return render_template("votermessage.html", alert = alert, message = message)
    else:
        return render_template("voterlogin.html")


@app.route("/voterlist", methods=["GET", "POST"])
@login_required
def voterlist():
    if request.method == "POST":

        election_id = request.form.get("hiddenElectionId")
        election = db.execute ("SELECT * FROM Elections WHERE election_id = ?", election_id)
        name = election[0]["name"]
        status = election[0]["status"]

        # Count the no. of voters in the voterlist
        voterlistname = db.execute("SELECT filename FROM Voterlists WHERE voterlist_id = (SELECT voterlist_id FROM Elections WHERE election_id = ?)", election_id)
        with open(voterlistname[0]["filename"], mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            votercount = 0
            for row in csv_reader:
                votercount += 1

        # Count the no. of votes casted
        votescastedrow = db.execute("SELECT COUNT(*) FROM Votes WHERE election_id = ?", election_id)
        votescasted = votescastedrow[0]["COUNT(*)"]

        quorum = election[0]["quorum"]
        votingpercent = (round(votescasted / votercount * 100, 2))
        startdate = election[0]["startdate"]
        enddate = election[0]["enddate"]
        todaytimestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        #create a list of total voters
        votescastedlist = db.execute ("SELECT * FROM Votes WHERE election_id = ?", election_id)
        voter_list = []
        with open(voterlistname[0]["filename"], mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                voter_list.append(row)
            for voter in voter_list:
                voter["vote"] = "--"
                voter["timestamp"] = "--"
                voter["vote_id"] = "--"
                for row in votescastedlist:
                    if (voter["Email Address"] == row["voter_emailaddress"]):
                        voter["vote"] = row["vote"]
                        voter["timestamp"] = row["votingdate"]
                        voter["vote_id"] = row["vote_id"]
                        if voter["vote"] == "1":
                            votervotequery = db.execute("SELECT option1 FROM Ballots WHERE election_id = ?", election_id)
                            voter["vote"] = votervotequery[0]["option1"]
                        if voter["vote"] == "2":
                            votervotequery = db.execute("SELECT option2 FROM Ballots WHERE election_id = ?", election_id)
                            voter["vote"] = votervotequery[0]["option2"]
                        if voter["vote"] == "3":
                            votervotequery = db.execute("SELECT option3 FROM Ballots WHERE election_id = ?", election_id)
                            voter["vote"] = votervotequery[0]["option3"]
        if len(voter_list) == 0:
            message = "There are no voters in this list."
        else:
            message = ""

    return render_template ("voterlist.html", name = name,
                                election_id = election_id,
                                status = status,
                                votercount = votercount,
                                votescasted = votescasted,
                                quorum = quorum,
                                votingpercent = votingpercent,
                                startdate = startdate,
                                enddate = enddate,
                                todaytimestamp = todaytimestamp,
                                voter_list = voter_list,
                                message = message)


@app.route("/voterlist_notvoted", methods=["GET", "POST"])
@login_required
def voterlist_notvoted():
    if request.method == "POST":

        election_id = request.form.get("hiddenElectionId")
        election = db.execute ("SELECT * FROM Elections WHERE election_id = ?", election_id)
        name = election[0]["name"]
        status = election[0]["status"]

        # Count the no. of voters in the voterlist
        voterlistname = db.execute("SELECT filename FROM Voterlists WHERE voterlist_id = (SELECT voterlist_id FROM Elections WHERE election_id = ?)", election_id)
        with open(voterlistname[0]["filename"], mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            votercount = 0
            for row in csv_reader:
                votercount += 1

        # Count the no. of votes casted
        votescastedrow = db.execute("SELECT COUNT(*) FROM Votes WHERE election_id = ?", election_id)
        votescasted = votescastedrow[0]["COUNT(*)"]

        quorum = election[0]["quorum"]
        votingpercent = (round(votescasted / votercount * 100, 2))
        startdate = election[0]["startdate"]
        enddate = election[0]["enddate"]
        todaytimestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        #create a list of total voters
        votescastedlist = db.execute ("SELECT * FROM Votes WHERE election_id = ?", election_id)
        voter_list = []
        with open(voterlistname[0]["filename"], mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                voter_list.append(row)
            for voter in voter_list:
                voter["vote"] = "--"
                voter["timestamp"] = "--"
                voter["vote_id"] = "--"
                for row in votescastedlist:
                    if (voter["Email Address"] == row["voter_emailaddress"]):
                        #delete row in voter_list
                        voter_list = [v for v in voter_list if v != voter]
        if len(voter_list) == 0:
            message = "There are no voters in this list."
        else:
            message = ""

    return render_template ("voterlist_notvoted.html", name = name,
                                election_id = election_id,
                                status = status,
                                votercount = votercount,
                                votescasted = votescasted,
                                quorum = quorum,
                                votingpercent = votingpercent,
                                startdate = startdate,
                                enddate = enddate,
                                todaytimestamp = todaytimestamp,
                                voter_list = voter_list,
                                message = message)

@app.route("/voterlist_voted", methods=["GET", "POST"])
@login_required
def voterlist_voted():
    if request.method == "POST":

        election_id = request.form.get("hiddenElectionId")
        election = db.execute ("SELECT * FROM Elections WHERE election_id = ?", election_id)
        name = election[0]["name"]
        status = election[0]["status"]

        # Count the no. of voters in the voterlist
        voterlistname = db.execute("SELECT filename FROM Voterlists WHERE voterlist_id = (SELECT voterlist_id FROM Elections WHERE election_id = ?)", election_id)
        with open(voterlistname[0]["filename"], mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            votercount = 0
            for row in csv_reader:
                votercount += 1

        # Count the no. of votes casted
        votescastedrow = db.execute("SELECT COUNT(*) FROM Votes WHERE election_id = ?", election_id)
        votescasted = votescastedrow[0]["COUNT(*)"]

        quorum = election[0]["quorum"]
        votingpercent = (round(votescasted / votercount * 100, 2))
        startdate = election[0]["startdate"]
        enddate = election[0]["enddate"]
        todaytimestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        #create a list of total voters
        votescastedlist = db.execute ("SELECT * FROM Votes WHERE election_id = ?", election_id)
        voter_list = []
        with open(voterlistname[0]["filename"], mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                voter_list.append(row)

            for voter in voter_list:
                voter["vote"] = "--"
                voter["timestamp"] = "--"
                voter["vote_id"] = "--"
                for row in votescastedlist:
                    if voter["Email Address"] == row["voter_emailaddress"]:
                        # Keep the row in voter_list
                        voter["vote"] = row["vote"]
                        voter["timestamp"] = row["votingdate"]
                        voter["vote_id"] = row["vote_id"]
                        if voter["vote"] == "1":
                            votervotequery = db.execute("SELECT option1 FROM Ballots WHERE election_id = ?", election_id)
                            voter["vote"] = votervotequery[0]["option1"]
                        elif voter["vote"] == "2":
                            votervotequery = db.execute("SELECT option2 FROM Ballots WHERE election_id = ?", election_id)
                            voter["vote"] = votervotequery[0]["option2"]
                        elif voter["vote"] == "3":
                            votervotequery = db.execute("SELECT option3 FROM Ballots WHERE election_id = ?", election_id)
                            voter["vote"] = votervotequery[0]["option3"]

            # Remove rows in voter_list where the email addresses do not match the condition
            voter_list = [voter for voter in voter_list if any(voter["Email Address"] == row["voter_emailaddress"] for row in votescastedlist)]

            if len(voter_list) == 0:
                message = "There are no voters in this list."
            else:
                message = ""

    return render_template ("voterlist_voted.html", name = name,
                                election_id = election_id,
                                status = status,
                                votercount = votercount,
                                votescasted = votescasted,
                                quorum = quorum,
                                votingpercent = votingpercent,
                                startdate = startdate,
                                enddate = enddate,
                                todaytimestamp = todaytimestamp,
                                voter_list = voter_list,
                                message = message)


@app.route("/voterlist_details", methods=["GET", "POST"])
@login_required
def voterlist_details():
    if request.method == "POST":
        voterlist_id = request.form.get('hiddenVoterlistId')

        voterlist = db.execute("SELECT * FROM Voterlists WHERE voterlist_id = ?", voterlist_id)
        voterlistname = voterlist[0]["voterlistname"]
        voterlistfilename = voterlist[0]["dbfilename"]
        uploaddate = voterlist[0]["uploaddate"]
        uploadtime = voterlist[0]["uploadtime"]
        voterlist_id = voterlist[0]["voterlist_id"]
        voter_list = []

        if voterlist:
            with open(voterlist[0]["filename"], mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    voter_list.append(row)

    return render_template("voterlist_details.html", voter_list = voter_list, voterlist_id = voterlist_id, voterlistname = voterlistname, voterlistfilename = voterlistfilename, uploaddate = uploaddate, uploadtime = uploadtime)


@app.route('/election_status', methods=['POST'])
def election_status():
    # Get the form data
    election_id = request.form.get('election_id')
    new_state = request.form.get('state')

    if new_state == 'start':
        db.execute("UPDATE Elections SET status = 'Active' WHERE election_id = ?", election_id)
        pass

    elif new_state == 'stop':
        db.execute("UPDATE Elections SET status = 'Inactive' WHERE election_id = ?", election_id)
        pass

    # Add a message to indicate the election status change
   # message = f'Election has {"started" if new_state == "start" else "stopped"}'

    return redirect("/")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/voterlogout")
def voterlogout():
    """Log voter out"""

    # Forget any user_id
    session.clear()

    message = "You have successfully logged out."

    # Redirect user to voter login form
    return render_template ("voterlogin.html", message = message)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    #User reached route via POST
    if request.method == "POST":

        #Ensure user was submitted
        if not request.form.get("email"):
            return apology("must provide email address", 400)

        #Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        #Ensure password confirmation is submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        #Ensure password and confirmation are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation do not match", 400)

        #Ensure username doesn't already exist
        rows = db.execute("SELECT * FROM Users WHERE email = ?", request.form.get("email"))
        if len(rows) != 0:
            return apology ("Email address already exists. Select a different email address", 400)

        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")
        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        organisation = request.form.get("organisation")
        designation = request.form.get("designation")
        db.execute("INSERT INTO Users (fname, lname, email, hash, organisation, designation) VALUES (?, ?, ?, ?, ?, ?)", fname, lname, email, password_hash, organisation, designation)

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/voterregistration", methods=["GET", "POST"])
def voterregistration():
    """Register a voter"""

    # Forget any user_id
    session.clear()
     #User reached route via POST
    if request.method == "POST":

   #Ensure user was submitted
        if not request.form.get("email"):
            return apology("must provide email address", 400)

        #Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        #Ensure password confirmation is submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        #Ensure password and confirmation are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation do not match", 400)

        #Ensure username doesn't already exist
        rows = db.execute("SELECT * FROM Voters WHERE email = ?", request.form.get("email"))
        if len(rows) != 0:
            return apology ("Email address already exists. Select a different email address", 400)

        email = request.form.get("email")
        password = request.form.get("password")
        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        db.execute("INSERT INTO Voters (email, hash) VALUES (?, ?)", email, password_hash)

        message = "You have successfully registered as a voter. Login to cast your vote."
        return render_template("voterlogin.html", message = message)

    else:
        return render_template("voterregistration.html")

@app.route("/delete_election", methods=["GET", "POST"])
def delete_election():
    if request.method == "POST":
        election_id = request.form.get("hiddenElectionId")
        db.execute("DELETE FROM Elections WHERE election_id = ?", election_id)
        return redirect ("/")
    else:
        return redirect ("/")

@app.route("/delete_voterlist", methods=["GET", "POST"])
def delete_voterlist():
    if request.method == "POST":
        voterlist_id = request.form.get("hiddenVoterlistId")
        voterlist = db.execute("SELECT * FROM Voterlists WHERE voterlist_id = ?", voterlist_id)
        filename = voterlist[0]["filename"]

        # Delete the file
        try:
            os.remove(filename)
            db.execute("DELETE FROM Voterlists WHERE voterlist_id = ?", voterlist_id)
            return redirect ("/")
        except OSError as e:
            return redirect ("/")
    else:
        return redirect ("/")

@app.route("/faqs", methods=["GET", "POST"])
def faqs():
    if request.method == "GET":
        return render_template("faqs.html")

@app.route("/aboutus", methods=["GET", "POST"])
def aboutus():
    if request.method == "GET":
        return render_template("aboutus.html")

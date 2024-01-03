# ELECTION YODA
#### Video Demo:  <https://www.loom.com/share/60c248b93f734c2fae13bdb7ab36350d?sid=03fa9e33-bf0c-4a30-97f0-92beea96198b>
#### Description:

## About Election Yoda:
ElectionYoda (named after a beloved Star Wars character) is a web application that enables a user to build and conduct an election online in a secure and transparent manner. In the current version, v1.0, the app helps the user by running a simple "majority wins" election in which the candidate with the highest votes wins. The app enables security and transparency through 256-bit encryption and the way they it is designed.

On a personal note, I am a big believer in democratic values and the right for people to choose their leaders in a free and fair manner. ElectionYoda is my attempt to shine a light in that area by providing an online tool for people to exercise this right.

## What Problem Are We Solving:
In my country, India, and across the world there are many small and large organisations that conduct internal elections to elect their leaders and office bearers. For many organisations this is a legal requirement and has to be done periodically. Many of these professional organisations like, for example, the Indian Orthopedics Association, is a national organistion of orthopedic surgeons with about 5,000 members distributed across the country. They conduct elections for the President and Secretary every year.
For this, they have to use online tools to run the election and report the results. ElectionYoda has been built for these type of organisations.

## How Big is the Market:
Internal elections are a legal requirement for any professional organisation in India and across the world. In addition, there are thousands of home-owners' associations, universities, colleges and schools that conduct elections to elect officer bearers and student governements. Further, there are internet communities that also could possibly need an app to run internal elections.

## The Product:
ElectionYoda is a web application built using Python, Javascript and SQL. It has two interfaces - The first is for a user that wants to build and run an election. In this the user can run multiple elections simultaneously and will have full control and real-time data over voting patterns. In the end, the app will show the election results in graphical format. The second interface is for the Voter who has been invited to vote in the election.

## Features:
* Easy to use - The UI/UX has been designed to make it very simple to use and interact with, even for a frist-time user and voter.
* Secure - The app is secured using a 256-bit encryption.
* Run multiple elections - A user can run multiple elections at the same time.
* No limit on the number of voters
* Transparent reporting - Users get real-time transparent reporting on voting patterns.


## Design and Architecture
The app is run on a single SQLite3 database with the ability to handle multiple users and voters. The front-end is designed using
HTML, CSS and Javascript and the back-end is built on Python using the Flask framework. In the current v1.0 the functionality of the app is limited in the following ways -
1. The user can only ask one ballot question with a maximum of 3 options.

## Technical Details
### Server-side
* app.py - the main python file with various flask routes and programming logic.
* helper.py - complimenting python file with functions to support the basic functionality of the app
* uploads directory - directory where the uploaded voterlist csv files are stored
* static directory - directory for styles.css and favicon
* templates directory - directory to store HTML templates

### Client-side (within templates folder)
**A. User interface -**
* index.html - User dashboard page
* register.html - User registration page
* login.html - User login page
* buildelection.html - Form to build an election
* electionhome.html - election dashboard with real-time voting data
* voterlist_upload.html - Form to upload a voterlist in .csv format
* voterlist_details.html - Page that opens and displays the contents of a voter list
* voterlist.html - Page that displays the detailed voting pattern for an election
* voterlist_voted.html - Page that displays all the voters that have cast their votes with vote details and a timestamp
* voterlist_notvoted.html - Page that displays all the voters that have not voted as yet
* success.html - Page to display a success message

**B. Voter interface -**
* voterregistration.html - Voter registration form
* voterlogin.html - Voter login form
* vote.html - Form to cast the vote
* votermessage.html - Page to display a confirmation messge

**C. Others**
* help.html - an FAQs page
* aboutus.html - brief introduction about the developer.

## About the developer:
* ElectionYoda was created by Devesh Taneja in 2023 as part of the final project requirement of Harvard's CS50 course requirement. This is v1.0 of the app. If you have any questions, you can reach me on devesh.taneja@gmail.com

## Usage

The application ships with a fairly permissive MIT license. You must agree to it in order to use the application.

The first thing to do after accepting the license is to set up your servers. Click the servers link on the left side and enter the details for a UAT or DEV server that you have available to you. Set up PROD too if you are feeling lucky.

Select Loaders from the left side navigation.

The application ships with a demo loader **Timekeeper HR Number** to illustrate how the process works. Briefly, we created some loader header information, then a list of attributes for that header. These correspond to an Elite 3E process details and some of the object fields. Once those have been entered, go to the Run tab and there is a grid to populate. The example is an illustration of what might happen if your payroll department switches systems and has assigned all new HR numbers which you need to update in 3E.

You can type directly in the grid or paste data in from Excel. Note the the columns can be moved around to assist if you've got them in a different order in an Excel sheet. There is no validation at this point; we're going to be handing all of this directly over to 3E to validate. The advanced tab also supports XOQL to pre-load the table with data. Pick the XOQL and hit the Load XOQL button.

Once you are all set, click the Run button. If you haven't already selected a Server to run this against, you'll be prompted to do so. So after you hit run, it may appear like nothing happened. Wait for moment just be on the safe side, then click the History tab. If you have many records in the data grid, this process can take considerable time depending on your local machine specs and server resources.

The History tab shows a log of previous (including the most recent) attempts to load data. It included the data as contained in the data grid, the Process XML passed to Elite 3E, and the response back from the Elite 3E server. If the history log is empty, something has gone wrong, or we haven't waited long enough. If the History is blank, Run the loader again and wait a little longer this time to see if the page reloads indicating it has completed.

I decided to ship the app with a debug setting on which results in a page full of errors if there were any major issues (like permissions, file access etc). As we polish things up a bit, we'll turn that debug setting off and catch and report all errors in a more friendly manner.

If everything did go correctly, you should be able to view a new entry in your 3E action list ready to submit (or cancel). If not, use the [GitHub Issues](https://github.com/junctionapps/elite3eloader/issues) feature to describe what went wrong and I'll do my best to assist.

## Screenshots
Look through the **docs** folder for some screenshots.
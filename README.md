<h1> Hi there! :) I've created a desktop GUI program that helps me delete various messages from my email. </h1>

It was created in a combination of Qt Creator 9.0.2 and python 3.10

The program filters messages based on the sender's address, which is located in data.txt. If a given message comes from the specified sender, it is deleted.

The program is currently able to work on several Polish email platforms and Gmail.

Feel free to use it, but remember a few things before you start:

1. Make sure that IMAP access is enabled on your email account, as it is necessary to log in to the mail.
2. If you want to log in to Gmail, you need to enable two-step authentication and generate a special password for the mail, which will allow you to log in. This is because Google blocks access to "less secure apps." The whole instruction can be found at the following link: https://support.google.com/accounts/answer/185833?hl=en . Once you generate a new password, use it to log in to Gmail in the program.
3. You choose which messages you want to delete. Therefore, before running the program, open the data.txt file and enter the sender's email addresses of the messages you want to delete. For example, if you want to delete messages from Netflix, go to the message source on your email, where you will find something like this: 'From: Netflix < info@members.netflix.com >'.
Then, write info@members.netflix.com to the data.txt file and that's all!
4. If you have thousands of messages, the deletion process may take several minutes depending on the mail server. Please be patient.
5. To make sure that all the messages you wanted to delete are actually deleted, use the program up to 3 times. This is because sometimes not all messages will be loaded when retrieving information from the mail server, regardless of my program's operation.

Enjoy it!

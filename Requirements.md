# Loan Platform

## Requirements:

1. Create a loan platform that allow customers to apply for a loan and keep track of the status of their application.
   A. Multi-step approval process - Analysis based on basic criteria - Credit verification - Loan Amount Qualification - Loan Document Preparation

   B. Business owner creates the login credentials (login and password)
   C. Loan Platform collects additional information such as: - Business credit reports - Bank Transactions - Non-Traditional data such as yelp reviews using the basic information provided

   D. Loan Platform has all the data it needs to make an automated loan decision.
   E. Decision is presented to the user, and if the user accepts the terms, the loan is funded.
   F. If the user logs back in after submitting a loan application, the system should present the current Application status (“Pending”, “Approved”, “Denied”) or Loan status (“Active”, “Closed”)
   G. If a loan has already been granted. If the loan is active, the application should display the remaining balance on their loan, past payment activity and pending payments.
   H. After a loan has been granted and funded, Loan Platform starts to collect payments daily.
   I. The funds collection process should be automatic. The application needs to create a daily file with all due payments. This file is then sent to the ACH network and the funds are eventually deposited in Loan Platform’s bank account.
   J. Next day, Loan Platform receives a file with all the transactions that could not be collected.
   K. The loan platform should process this file and update the payment status accordingly.

Loan decision:

1. If requested_amount > 50000 then Declined
2. If requested_amount = 50000 then Undecided
3. If requested_amount < 50000 then Approved

## Table:

- User
- Loan
- Payment
- Business
- Business_owner
- Loan_applications
- Loan_offers
- Bank_account
- Bank_transaction
- Credit_reports
- Alternative_data
- Ach_batch
- Ach_transactions
- Notifications

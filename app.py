import pandas as pd
import flask
from flask import Flask, render_template, request
import pickle
import numpy as np
from datetime import datetime
from datetime import date
from sklearn.preprocessing import StandardScaler

app = Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/static')
ind_model = pickle.load(open('indi_model.pkl', 'rb'))
jnt_model = pickle.load(open('jnt_model.pkl', 'rb'))


@app.route('/')
def main():
    return (flask.render_template('index.html'))

@app.route('/loanpred')
def loanprediction():
    return (flask.render_template('loanpred.html'))


@app.route('/individual', methods=['POST', 'GET'])
def individual():
    if flask.request.method == 'GET':
        return (flask.render_template('individual.html'))
    if flask.request.method == 'POST':
        earliest_cr_line_dt = pd.to_datetime(request.form.get('earliest_credit_line'))

        earliest_cr_line = int(earliest_cr_line_dt.strftime('%m%y'))

        annual_income = float(request.form.get('Annual_income'))

        zip_code = int(request.form.get('Zip_code'))

        mort_account = int(request.form.get('mort_account'))

        Fico_score = int(request.form.get('Fico_score'))

        open_account = int(request.form.get('open_account'))

        loan_amount = float(request.form.get('loan_amount'))

        total_account = int(request.form.get('total_account'))

        loan_term = int(request.form.get('term'))

        term = int(request.form.get('term').replace("36", '0').replace("60", '1'))

        verification_status = request.form.get('verification_status').replace("Source Verified", '0').replace("Not Verified", '2').replace("Verified", '1')
        verification_status = int(verification_status)

        dti = float(request.form.get('dti'))

        revol_util = float(request.form.get('revol_util'))

        home_ownership = int(request.form.get('home_ownership').replace("NONE", '0').replace('OTHER', '1').replace('ANY', '2').replace('OWN', '3').replace('RENT', '4').replace('MORTGAGE', '6'))


        credit_ratio = round(open_account / total_account, 2)

        issue_d_dt = datetime.strptime(date.today().strftime("%m/%d/%Y"), '%m/%d/%Y')
        issue_d = int(issue_d_dt.strftime('%m%y'))

        credit_history_dt = issue_d_dt - earliest_cr_line_dt
        credit_history = credit_history_dt.days
        installment = loan_amount / loan_term

        installment_ratio = round(installment / loan_amount,2)

    # we dont have values for columns like grade ,sub grade


    # scaling our values before prediction

        int_features = [earliest_cr_line, annual_income, zip_code, mort_account, Fico_score, open_account, loan_amount,
                        issue_d, credit_history,
                        total_account, term, verification_status, dti, revol_util, home_ownership, credit_ratio,
                        installment, installment_ratio]
        final = [np.array(int_features)]
        x_train=pd.read_csv("ind_train.csv",usecols=range(1,19))

        scaler = StandardScaler()
        scaler.fit(x_train)
        final = scaler.transform(final)

        prediction = ind_model.predict_proba(final)
        output=round(prediction[0][0],3)

        if dti> 40.0:
            return render_template('individual.html',pred='sorry your loan is denied because your Debt to income is too high')
        elif revol_util>89:
            return render_template('individual.html', pred='sorry your loan is denied because your credit amount usage is too high')
        elif output > 0.40:
            return render_template('individual.html', pred=f'"OOPS" sorry your loan is denied, your loan risk probabilty is : {output*100}% ')
        else:
            return render_template('individual.html', pred=f'"Congratulation",Your loan is approved \n\n your credit ratio is :{credit_ratio} \n\n   your installment_ratio is : {installment_ratio} \n\n   your credit_history: {credit_history} days \n\t  your loan risk probabilty : {output*100}% ')


@app.route('/joint', methods=['POST', 'GET'])
def joint():
    if flask.request.method == 'GET':
        return (flask.render_template('joint.html'))
    if flask.request.method == 'POST':
        earliest_cr_line_dt = pd.to_datetime(request.form.get('earliest_credit_line'))

        earliest_cr_line = int(earliest_cr_line_dt.strftime('%m%y'))

        annual_income = float(request.form.get('Avg_Annual_income'))

        zip_code = int(request.form.get('Zip_code'))

        mort_account = int(request.form.get('mort_account'))

        Fico_score = int(request.form.get('Fico_score'))

        open_account = int(request.form.get('open_account'))

        loan_amount = float(request.form.get('loan_amount'))

        total_account = int(request.form.get('total_account'))

        loan_term = int(request.form.get('term'))

        term = int(request.form.get('term').replace("36", '0').replace("60", '1'))

        verification_status = request.form.get('verification_status').replace("Source Verified", '0').replace("Not Verified", '2').replace("Verified", '1')
        verification_status = int(verification_status)

        dti = float(request.form.get('avg_dti'))

        revol_util = float(request.form.get('revol_util'))

        home_ownership = int(request.form.get('home_ownership').replace("NONE", '0').replace('OTHER', '1').replace('ANY', '2').replace('OWN', '3').replace('RENT', '4').replace('MORTGAGE', '6'))


        credit_ratio = round(open_account / total_account, 2)

        issue_d_dt = datetime.strptime(date.today().strftime("%m/%d/%Y"), '%m/%d/%Y')
        issue_d = int(issue_d_dt.strftime('%m%y'))

        credit_history_dt = issue_d_dt - earliest_cr_line_dt
        credit_history = credit_history_dt.days
        installment = loan_amount / loan_term

        installment_ratio = round(installment / loan_amount,2)

    # we dont have values for columns like grade ,sub grade


    # scaling our values before prediction

        int_features = [earliest_cr_line, annual_income, zip_code, mort_account, Fico_score, open_account, loan_amount,
                        issue_d, credit_history,
                        total_account, term, verification_status, dti, revol_util, home_ownership, credit_ratio,
                        installment, installment_ratio]
        final_j = [np.array(int_features)]
        x_train_j=pd.read_csv("jnt_train.csv",usecols=range(1,19))

        scaler = StandardScaler()
        scaler.fit(x_train_j)
        final = scaler.transform(final_j)

        prediction_j = jnt_model.predict_proba(final_j)
        output_j=round(prediction_j[0][1],3)

        if dti> 40.0:
            return render_template('joint.html',pred='sorry your loan is denied because your Debt to income is too high')
        elif revol_util>89:
            return render_template('joint.html', pred='sorry your loan is denied because your credit amount usage is too high')
        elif output_j > 0.40:
            return render_template('joint.html', pred=f'"OOPS" sorry your loan is denied, your loan risk probabilty is : {output_j*100}%')
        else:
            return render_template('joint.html', pred=f'"Congratulation",Your loan is approved \n\n your credit ratio is :{credit_ratio} \n\n  your installment_ratio is : {installment_ratio} \n\n  your credit_history: {credit_history} days \n\t  your loan risk probabilty is : {output_j*100}%')


if __name__ == '__main__':
    app.run(debug=True)

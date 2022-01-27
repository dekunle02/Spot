import unittest
from datetime import datetime

from Spot.compose import composer
from Spot.database.models import User, TimeSheet, NightDisturbance


class ComposerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.html = """     
<!doctype html>
<html lang="en">
<head>
</head>
<body>
</body>
</html>
        """
        self.user = User(
            id='1',
            first_name="a",
            last_name="b",
            hospital_name="c",
            signature_file_id="d"
        )

        start = datetime.fromisoformat("2022-01-26 13:00:00.000")
        end = datetime.fromisoformat("2022-02-02 13:00:00.000")

        self.timesheet = TimeSheet(
            user=self.user,
            shift_start=start,
            shift_end=end
        )

        self.timesheet.append_nightDisturbance(NightDisturbance(
            time=start,
            duration='3min',
            reason="a"
        ))
        self.timesheet.append_nightDisturbance(NightDisturbance(
            time=end,
            duration='4min',
            reason="b"
        ))

        return super().setUp()

    """ insertion_func_list = [insert_css, insert_biodata, insert_work_rows,
                           insert_total_hours, insert_signing_date, insert_night_disturbances, insert_signature]
  """

    def test_get_html_template(self):
        """Can get the html from the assets directory"""
        expected_html_string = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter&display=swap">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    XXCSSXX
    <title>Timesheet</title>
</head>

<body>
    <div class="heading">
        <span class="heading__title">24/7 Timesheet / Night Disturbances Record</span>
        <div class="heading__logo-box">
            <img src="https://neshealthcare.co.uk/wp-content/uploads/2018/02/logo.png" alt="nes_logo">
        </div>
    </div>

    <div class="content">

        <div class="main-block">
            <div class="bio-data">
                <div class="bio-data__row">
                    <span> <span class="bold-text">First name:</span> <span>XXFIRST_NAMEXX</span> </span>
                    <span> <span class="bold-text">Surname:</span> <span>XXLAST_NAMEXX</span> </span>
                </div>

                <span> <span class="bold-text">Hospital:</span> <span>XXHOSPITALXX</span> </span>
            </div>
            <div class="timesheet__title-block">
                <h5 class="minor-title-text"> Timesheet </h5>
                <span class="minor-bold-text">Please claim only for hours worked:</span>
            </div>

            <div class="timesheet__table">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th scope="col"></th>
                            <th scope="col">Date</th>
                            <th scope="col">Start time</th>
                            <th scope="col">Finish time</th>
                            <th scope="col">Total hours</th>
                        </tr>
                    </thead>
                    <tbody>
                        XXWORK_ROWSXX
                        <tr>
                            <td colspan="4" align="end" class="minor-bold-text">Total weekly hours</td>
                            <td>XXTOTAL_WEEK_HOURSXX</td>
                        </tr>
                    </tbody>
                </table>
    
            </div>
         
            <div class="timesheet__footer-block">
                <ul>
                    <li><span>Your shift will start as soon as you take the bleep from the current RMO, and will
                            end as soon as you pass it back to them.</span></li>
                    </li>
                    <li> <span>
                            Please either <span class="bold-text">FAX</span> this timesheet to <span
                                class="bold-text">01296 746155</span> or <span class="bold-text">EMAIL</span> your
                            timesheets to
                            your <a href="#">timesheets@neshealthcare.co.uk</a>. This should be done immediately after
                            finishing your shift. Failure to do so could result in non-payment.
                        </span>
                    </li>
                    <li><span>On occasion we have doctors claiming for the same hours. To avoid confusion
                            please agree the time of changeover with your colleague.</span></li>
                    </li>
                    <li><span>Please ensure you have written your name and hospital at the top of this form.

                    </li>


                </ul>
            </div>


        </div>

        <div class="side-block">
            <div class="night-block__heading">
                <h5 class="minor-title-text">Night disturbances (2400 to 0600)</h5>
                <span class="minor-bold-text">Please log any night calls during this week below:</span>
            </div>

            <div>

            </div>
            <table class="table table-bordered night-block__table">
                <thead>
                    <tr>
                        <th scope="col">Date</th>
                        <th scope="col">Time</th>
                        <th scope="col">Duration</th>
                        <th scope="col">Brief reason(e.g pain, cannulation) </th>
                    </tr>
                </thead>
                <tbody>
                    XXDISTURBANCE_ROWSXX
                </tbody>
            </table>

            <div class="declaration-block">
                <div class="declaration-block__heading">
                    <h5 class="minor-title-text">Declaration</h5>
                    <span class="minor-bold-text">I hereby confirm that the hours claimed are correct.</span>
                </div>

                <div class="declaration-block__signature">
                    <span> <span class="minor-bold-text">RMO signature:</span>
                        <div class="signature-box">
                            <img src="XXSIGNATUREXX" alt="">
                        </div>
                    </span>
                    <span> <span class="minor-bold-text">Date: </span>XXSIGNATURE_DATEXX</span>
                </div>
            </div>

        </div>

    </div>
</body>


</html>"""
        self.assertEqual(expected_html_string, composer.extract_html_string())

    def test_insert_css(self):
        """css is read from the directory and inserted into a string"""
        expected_result = """<style>
*,
*::after,
*::before {
  margin: 0;
  padding: 0;
  box-sizing: inherit;
}

html {
  font-size: 62.5%;
}

td {
  height: 3rem;
}

body {
  box-sizing: border-box;
  line-height: 1.7;
  font-family: "Inter", sans-serif;
  padding: 5rem 5rem;
}

img {
  max-width: 100%;
  max-height: 100%;
}

.bold-text {
  font-weight: 600;
  font-size: 1.4rem;
}
.minor-title-text {
  color: rgba(2, 83, 164, 255);
  font-weight: 600;
  font-size: 1.4rem;
}
.minor-bold-text {
  font-weight: 550;
  font-size: 1.2rem;
}

/* HEADER */
.heading {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.heading__title {
  font-size: 2rem;
  font-weight: 600;
  color: rgba(2, 83, 164, 255);
}

.heading__logo-box {
  display: inline-block;
  /* height: 15rem; */
  width: 15rem;
}

/* LAYOUT */

.content {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.main-block {
  width: 40vw;
}

.side-block {
  width: 45vw;
  padding: 0 2rem;
}

/* BIODATA */

.bio-data {
  width: 80%;
  display: flex;
  flex-direction: column;
}

.bio-data__row {
  display: flex;
  padding: 2rem 0;
  flex-direction: row;
  justify-content: space-between;
}

.timesheet__title-block {
  padding: 1.5rem 0;
}

.timesheet__table {
  margin-right: 2rem;
}

.timesheet__footer-block {
  margin: 0 auto;
  width: 90%;
  font-weight: 500;
  font-size: 1.3rem;
  margin-top: 2rem;
}

.night-block__heading {
  padding: 2rem 0;
}

.night-block__table {
  margin: 0 2rem;
}

.declaration-block {
  margin-top: 2rem;
}

.declaration-block__signature {
  display: flex;
  flex-direction: row;
  margin: 2rem 0;
  align-items: center;
}

.signature-box {
  display: inline-block;
  width: 15rem;
}
</style>"""
        self.assertEqual(expected_result, composer.insert_css("XXCSSXX"))

    def test_insert_biodata(self):
        template = "XXXXFIRST_NAMEXX=XXLAST_NAMEXX=XXHOSPITALXX"
        expected_result = "a=b=c"
        self.assertEqual(expected_result, composer.insert_biodata(template, self.user))

    
<?php

$con = mysqli_connect("hldbv02", "ronm", "a1a1a1", "tecan");

// Check connection
if (mysqli_connect_errno())
{
    exit("Failed to connect to MySQL: " . mysqli_connect_error());
}

// Check input arguments
if (!array_key_exists("exp_condition", $_GET))
{
    exit("Must provide key for exp_condition");
}
$exp_condition = $_GET["exp_condition"];

if (!array_key_exists("merged_exp_id", $_GET))
{
    exit("Must provide key for merged_exp_id");
}
$merged_exp_id = $_GET["merged_exp_id"];

if (!array_key_exists("description", $_GET))
{
    $description = "";
}
else
{
    $description = $_GET["description"];
}

// Instert merged data into database
$query = "INSERT INTO tecan_readings (exp_id, plate, reading_label, row, col, time, measurement)
          SELECT      \"$merged_exp_id\" exp_id, 0 plate, reading_label, row, col, time, measurement
          FROM        tecan_readings 
          WHERE       $exp_condition 
          ORDER BY time, plate, reading_label, row, col;";
$result = mysqli_query($con, $query);
#echo "<p>$query</p>";

$query = "INSERT INTO tecan_experiments VALUES (\"$merged_exp_id\", \"MERGE\", \"$description\");";
$result = mysqli_query($con, $query);
#echo "<p>$query</p>";

$query = "INSERT INTO tecan_plates VALUES (\"$merged_exp_id\", 0, \"\", NULL, NULL);";
$result = mysqli_query($con, $query);
#echo "<p>$query</p>";

$query = "INSERT INTO tecan_labels (exp_id, plate, row, col, label)
          SELECT      \"$merged_exp_id\" exp_id, 0 plate, row, col, label 
          FROM        tecan_labels
          WHERE       $exp_condition 
          GROUP BY    row, col;";
$result = mysqli_query($con, $query);
#echo "<p>$query</p>";

echo "GREAT SUCCESS!!! The experiments have been merged to the new Exp. ID: $merged_exp_id</br>";
echo "Select other experiments to merge: <a href='exp_list.php'>Experiment list</a></br>";
?>

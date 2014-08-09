<?php

$con = mysqli_connect("hldbv02", "ronm", "a1a1a1", "tecan");

// Check connection
if (mysqli_connect_errno())
{
    exit("Failed to connect to MySQL: " . mysqli_connect_error());
}

// Check input arguments
if (!array_key_exists("exp_id", $_GET))
{
    exit("Must provide keys for exp_id and merged_exp_id");
}

if (!array_key_exists("merged_exp_id", $_GET))
{
    exit("Must provide key for merged_exp_id");
}
$merged_exp_id = $_GET["merged_exp_id"];

$query = "SELECT count(*) FROM tecan_experiments WHERE exp_id = \"$merged_exp_id\"";

$result = mysqli_query($con, $query);
$row = mysqli_fetch_array($result);
if ($row[0] > 0)
{
    echo $row;
    echo "There is already an experiment with the ID <b>$merged_exp_id</b> 
          please go back to the <a href='exp_list.php'>Experiment list</a> 
          and provide a new ID";
}
else
{
    $tmp = explode("__", $_GET["exp_id"][0], 2);
    $exp_condition = "(exp_id = \"$tmp[0]\" AND plate = $tmp[1])";
    echo $description;
    for ($i = 1; $i < count($_GET["exp_id"]); ++$i)
    {
        $tmp = explode("__", $_GET["exp_id"][$i], 2);
        $exp_condition = $exp_condition . " OR (exp_id = \"$tmp[0]\" AND plate = $tmp[1])";
    }
    
    $exp_condition = "($exp_condition)";
    $query = "SELECT   exp_id, plate, min(time) start_time, max(time) end_time, count(*) cnt FROM (
                   SELECT   exp_id, plate, time FROM tecan_readings
                   WHERE    $exp_condition
                   GROUP BY exp_id, plate, time 
                   ) tecan_times
              GROUP BY exp_id, plate
              ORDER BY start_time";
    #echo "<p>$query</p>";
    $result = mysqli_query($con, $query);
    echo "<table border='1'>";
    echo "<tr>";
    echo "<th>Exp. ID</th>";
    echo "<th>Plate</th>";
    echo "<th>Start Time</th>";
    echo "<th>End Time</th>";
    echo "<th>Duration</th>";
    echo "<th># Cycles</th>";
    echo "</tr>\n";

    $first_start_time = false;
    $last_end_time = 0;
    while($row = mysqli_fetch_array($result))
    {
        if (!$first_start_time) { $first_start_time = $row['start_time']; }
        $last_end_time = $row['end_time'];
        
        echo "<tr>";
        echo "<td><i>" . $row['exp_id'] . "</i></td>";
        echo "<td>" . $row['plate'] . "</td>";
        echo "<td>" . date("Y-m-d H:i:s", $row['start_time']) . "</td>";
        echo "<td>" . date("Y-m-d H:i:s", $row['end_time']) . "</td>";
        echo "<td>" . round(($row['end_time'] - $row['start_time'])/3600, 1) . " h</td>";
        echo "<td>" . $row['cnt'] . "</td>";
        echo "</tr>\n";
    }
    echo "</table>";
    $description = date("Y-m-d H:i:s", $first_start_time)." => ".date("Y-m-d H:i:s", $last_end_time);
    
    echo "<p><b>Click on the following link to confirm the merge: </br> ";
    $url = "merge_confirm.php?merged_exp_id=".urlencode($merged_exp_id)."&exp_condition=".urlencode($exp_condition)."&description=".urlencode($description);
    echo "<a href=\"$url\">$merged_exp_id</a>";
}

?>

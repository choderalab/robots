<?php
#date_default_timezone_set('Etc/GMT');

$con=mysqli_connect("hldbv02","ronm","a1a1a1","tecan");
// Check connection
if (mysqli_connect_errno())
{
    echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$query = "SELECT e.exp_id, e.plate, e.row, e.col, e.time, e.time - min(r.time) time_diff
          FROM   exp_induction_log e , tecan_readings r
          WHERE  e.exp_id = r.exp_id 
          AND    e.plate = r.plate
          AND    e.row = r.row
          AND    e.col = r.col
          AND    r.reading_label = 'OD600'
          GROUP BY e.exp_id, e.plate, e.row, e.col
          ORDER BY e.time DESC";

$result = mysqli_query($con, $query);

echo "<table border='1'>\n";
echo "<tr>\n";
echo "<th>Exp. ID</th>\n";
echo "<th>Plate</th>\n";
echo "<th>Row</th>\n";
echo "<th>Column</th>\n";
echo "<th>Induction Time</th>\n";
echo "<th>Induction Time (hours since exp. started)</th>\n";
echo "</tr>\n";

while($row = mysqli_fetch_array($result))
{
    $id = $row['exp_id'] . "__" . $row['plate'];
    echo "<tr>";
    echo "<td>" . $row['exp_id'] . "</td>";
    echo "<td>" . $row['plate'] . "</td>";
    echo "<td>" . $row['col'] . "</td>\n";
    echo "<td>" . $row['row'] . "</td>";
    echo "<td>" . date("Y-m-d H:i:s", $row['time']) . "</td>";
    echo "<td>" . round($row['time_diff']/3600, 1) . "</td>";
    echo "</tr>";
}
echo "</table>";


mysqli_close($con);
?>

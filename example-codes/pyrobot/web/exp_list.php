<?php
#date_default_timezone_set('Etc/GMT');

$con=mysqli_connect("hldbv02","ronm","a1a1a1","tecan");
// Check connection
if (mysqli_connect_errno())
{
    echo "Failed to connect to MySQL: " . mysqli_connect_error();
}

$query = "SELECT exp_id, plate, description, owner, project 
          FROM tecan_plates
          ORDER BY exp_id DESC, plate";
$result = mysqli_query($con, $query);

$default_exp_id = date("Y-m-d H:i:s");

echo "<p><form name=\"input\" action=\"merge.php\" method=\"get\">";
echo "Merged exp_id: <input type=\"text\" size=\"30\" name=\"merged_exp_id\" value=\"$default_exp_id\">";
echo "<input type=\"submit\" value=\"Submit\"></p>";

echo "<table border='1'>\n";
echo "<tr>\n";
echo "<th></th>\n";
echo "<th>Exp. ID</th>\n";
echo "<th>Plate</th>\n";
echo "<th>Description</th>\n";
echo "<th>Owner</th>\n";
echo "<th>Project</th>\n";
echo "</tr>\n";

while($row = mysqli_fetch_array($result))
{
    $id = $row['exp_id'] . "__" . $row['plate'];
    echo "<tr>";
    echo "<td><input type=\"checkbox\" name=\"exp_id[]\" value=\"$id\"></td>";
    echo "<td>" . $row['exp_id'] . "</td>";
    echo "<td>" . $row['plate'] . "</td>";
    echo "<td>" . $row['description'] . "</td>\n";
    echo "<td>" . $row['owner'] . "</td>";
    echo "<td>" . $row['project'] . "</td>";
    echo "</tr>";
}
echo "</table>";

mysqli_close($con);
?>

<!DOCTYPE html>
 <head>
  <link rel="stylesheet" type="text/css" href="parkinfo.css">
 </head>
 <body>
   <p>
     <?php

     function get($loc) {
       global $redis;
       $val = $redis->get($loc);
       if ($val == null) {
         $val = "empty";
       }
       return $val;
     }

     $username = $_SERVER["PHP_AUTH_USER"];
     if ($_SERVER["REQUEST_METHOD"] == "POST") {
       $locs = array("stephens","synge","westland","kildare");
       $redis = new Redis();
       $redis->connect('127.0.0.1', 6379);
       for ($i=0; $i<4; $i++) {
         $val = get($locs[$i]);
         if ($val == $username) {
	    $redis->set($locs[$i],"empty");
            echo "Parking space at ";
	    switch ($locs[$i]) {
              case "stephens": echo "85 St. Stephens Green"; break;
              case "synge": echo "33 Synge Street"; break;
              case "westland": echo "21 Westland Row"; break;
              case "kildare": echo "2/3 Kildare Street"; break;
            }
            echo " has been marked as empty.";
	    break;
	 }
       }
       if ($val != $username) {
	 echo "You do not have a reserved parking place.";
       }
     }
    ?>
  </p>

  <form action="/parkinfo.php" method="get" id="controls"> 
    <input type="submit" value="Done">
  </form>
 </body>
</html>

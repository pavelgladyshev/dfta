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

     $username=$_SERVER["PHP_AUTH_USER"];
     if ($_SERVER["REQUEST_METHOD"] == "POST") {
       $locs = array("stephens","synge","westland","kildare");
       $loc = htmlspecialchars($_POST["loc"]);
       if (in_array($loc,$locs)) {
         $redis = new Redis();
         $redis->connect('127.0.0.1', 6379);
	 $val = get($loc);
	 for ($i=0; $i<4; $i++) {
           $val = get($locs[$i]);
           if ($val == $username) {
             echo "You have already reserved ";
             switch ($locs[$i]) {
               case "stephens": echo "85 St. Stephens Green"; break;
               case "synge": echo "33 Synge Street"; break;
               case "westland": echo "21 Westland Row"; break;
               case "kildare": echo "2/3 Kildare Street"; break;
             }
             echo ".";
             break;
           }
	 }
	 if ($val != $username) {
	   echo "Parking space at ";
	   switch ($loc) {
             case "stephens": echo "85 St. Stephens Green"; break;
	     case "synge": echo "33 Synge Street"; break;
	     case "westland": echo "21 Westland Row"; break;
	     case "kildare": echo "2/3 Kildare Street"; break;
	   }
	   $val = get($loc);
	   if ($val == "empty") {
             $redis->set($loc,$username);
	     echo " is now reserved for user ". $username .".";
  	   } else {
	     echo " is already occupied by the user ". $val .", please choose another parking space.";
	   }  
	 }
       }
     }
    ?>
  </p>

  <form action="/parkinfo.php" method="get" id="controls"> 
    <input type="submit" value="Done">
  </form>
 </body>
</html>

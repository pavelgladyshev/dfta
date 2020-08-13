<!DOCTYPE html>
 <head>
  <link rel="stylesheet" type="text/css" href="parkinfo.css">
 </head>
 <body>
   <?php
     function get($loc) {
       global $redis;
       $val = $redis->get($loc);
       if ($val == null) {
         $val = "empty";
       }
       return $val;
     }

     $locs = array("stephens","synge","westland","kildare");   
     $redis = new Redis();
     $redis->connect('127.0.0.1', 6379);
     $stephens = get("stephens"); 
     $synge = get("synge"); 
     $westland = get("westland");  
     $kildare = get("kildare"); 
     $username = $_SERVER['PHP_AUTH_USER'];
   ?>
   <h1> Parking Information</h1>
   <div id="info">
     <table>
     <tr>
       <th>85 St. Stephens Green</th>
       <th><?php echo $stephens; ?></th>
    </tr>
    <tr>
       <th>33 Synge Street</th>
       <th><?php echo $synge; ?></th>
    </tr>
    <tr>
       <th>21 Westland Row</th>
       <th><?php echo $westland; ?></th>
    </tr>
    <tr>
       <th>2/3 Kildare Street</th>
       <th><?php echo $kildare; ?></th>
    </tr>
    </table>
  </div>
  <form action="/reserve.php" method="POST"> 
    <label for="loc">Choose parking space location:</label><br>
    <select id="loc" name="loc">
       <option value="stephens">85 St. Stephens Green</option>
       <option value="synge">33 Synge Street</option>
       <option value="westland">21 Westland Row</option>
       <option value="kildare">2/3 Kildare Street</option>
    </select>
    <input type="submit" value="Reserve">
  </form>

  <form action="/release.php" method="POST">
    <input type="submit" value="Release">
  </form>
 </body>
</html>

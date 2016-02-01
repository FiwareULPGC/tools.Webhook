<?php
require 'Slim-2.6.2/Slim/Slim.php';
\Slim\Slim::registerAutoloader();

$app = new \Slim\Slim();
 
$app->contentType('application/json; charset=utf-8');
 
$app->get('/', function() {
            echo "Welcome to mirror-webhook.";
        });
  
$app->post('/hook',function() use($app){
            $body = $app->request->getBody();

            $myfile = fopen("/var/tmp/hook-request.txt", "w") or die("Unable to open file!");

            fwrite($myfile, $body);
            fwrite($myfile, "\n");

            fclose($myfile);

            $output = shell_exec("sudo -u fiwareulpgc /home/fiwareulpgc/mirrors/script/update-mirror.py '".$body."'");

            echo $body;

            $app->response->setStatus(200);
});

$app->post('/deny-pull-request',function() use($app){
            $body = $app->request->getBody();

            $myfile = fopen("/var/tmp/pull-request.txt", "w") or die("Unable to open file!");

            fwrite($myfile, $body);
            fwrite($myfile, "\n");

            fclose($myfile);

            $output = shell_exec("sudo -u fiwareulpgc /home/fiwareulpgc/mirrors/script/deny-pull-requests.py '".$body."' /home/fiwareulpgc/mirrors/script/utils/token-fiware.txt");

            echo $body;

            $app->response->setStatus(200);
});
 
$app->run();
?>

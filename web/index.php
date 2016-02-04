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

            $update_script = "/home/fiwareulpgc/mirrors/script/update-mirror.py";

            $output = shell_exec("sudo -u fiwareulpgc ".$update_script." '".$body."'");

            echo $body;

            $app->response->setStatus(200);
});

$app->post('/deny-pull-request',function() use($app){
            $body = $app->request->getBody();

            $deny_script = "/home/fiwareulpgc/mirrors/script/deny-pull-requests.py";
            $github_token_file = "/home/fiwareulpgc/mirrors/script/utils/token-fiware.txt";

            $output = shell_exec("sudo -u fiwareulpgc ".$deny_script." '".$body."' ".$github_token_file);

            echo $body;

            $app->response->setStatus(200);
});
 
$app->run();
?>

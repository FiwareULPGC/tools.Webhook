<?php
require 'Slim-2.6.2/Slim/Slim.php';
\Slim\Slim::registerAutoloader();

$app = new \Slim\Slim();

$app->contentType('application/json; charset=utf-8');

$app->get('/', function() {
            echo "Welcome to mirror-webhook.";
        });
  
$app->post('/hook',function() use($app){

    $update_script = "/home/fiwareulpgc/mirrors/script/update-mirror.py";
    $github_token_file = "/home/fiwareulpgc/mirrors/script/utils/github-token";
    $event = $app->request->headers->get('X-GitHub-Event');
    $body = $app->request->getBody();

    $command = "sudo -u fiwareulpgc ".$update_script." '".$event."'";
    $command .= " '".$body."' ".$github_token_file." 2>&1";

    exec($command, $output, $return_var);

    if ($return_var == 0){
        echo "OK";
        $app->response->setStatus(200);
    }
    else{
        error_log(implode("\n", $output));
        echo "Internal server error";
        $app->response->setStatus(500);
    }

});

$app->post('/deny-pull-request',function() use($app){

    $deny_script = "/home/fiwareulpgc/mirrors/script/deny-pull-requests.py";
    $github_token_file = "/home/fiwareulpgc/mirrors/script/utils/github-token";
    $body = $app->request->getBody();

    $command = "sudo -u fiwareulpgc ".$deny_script;
    $command .= " '".$body."' ".$github_token_file." 2>&1";

    exec($command, $output, $return_var);

    if ($return_var == 0){
        echo "OK";
        $app->response->setStatus(200);
    }
    else{
        error_log(implode("\n", $output));
        echo "Internal server error";
        $app->response->setStatus(500);
    }
});

$app->run();
?>

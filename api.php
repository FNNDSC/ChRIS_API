<?php
/**
 *
 *    _____ _    ______ _____ _____   _   _ _ _
 *   /  __ \ |   | ___ \_   _/  ___| | | | | | |
 *   | /  \/ |__ | |_/ / | | \ `--.  | | | | | |_ _ __ ___  _ __
 *   | |   | '_ \|    /  | |  `--. \ | | | | | __| '__/ _ \| '_ \
 *   | \__/\ | | | |\ \ _| |_/\__/ / | |_| | | |_| | | (_) | | | |
 *    \____/_| |_\_| \_|\___/\____/   \___/|_|\__|_|  \___/|_| |_|
 *
 * (c) 2015 Fetal-Neonatal Neuroimaging & Developmental Science Center
 *                   Boston Children's Hospital
 *
 *              http://childrenshospital.org/FNNDSC/
 *                        dev@babyMRI.org
 *
 *
 * This api.php is the main interface between the front end "view" and the
 * back end "model/controller" components.
 *
 *
 */

namespace ChRIS {

    class API_handler {

        public $payload = null;

        public function __construct($URL = null) {
            if(isset($URL)) {
                parse_str($URL, $_GET);
                parse_str($URL, $_POST);
            }
            $this->payload = array(
                'id'                => null,
                'status'            => 'not-processed',
                'username'          => 'unknown',
                'userid'            => -1,
                'timestamp'         => '',
                'execution_time'    => 0,
                'object'            => null,
                'method'            => null,
                'parameters'        => null,
                'str_return'        => null,
                'ar_return'         => null,
                'return_val'        => -1
            );
        }

        public function URL_parse($str_component) {
            if(isset($_GET[$str_component])){
                $this->payload[$str_component] = $_GET[$str_component];
            } else if(isset($_POST[$str_component])) {
                $this->payload[$str_component] = $_POST[$str_component];
            }
        }

        public function feed_handle() {
            switch($this->payload['method']) {
                case 'new':
                    exec('feed.py', $this->payload['ar_return'], $this->payload['return_val']);
                    $this->payload['str_return'] = implode("\n", $this->payload['ar_return']);
                    break;
            }
        }

        public function object_handle() {
            switch($this->payload['object']) {
                case 'Feed':
                    $this->feed_handle();
                    break;
            }
        }

        public function URL_handle() {
            $this->object_handle();
        }

        public function run() {

            $this->URL_parse('object');
            $this->URL_parse('method');
            $this->URL_parse('parameters');

            $this->URL_handle();

            print_r($this->payload);
        }

    }


    // main
    date_default_timezone_set('America/New_York');
    $time_start = new \DateTime();

    $handler = new API_handler($argv[1]);
    $handler->run();
}

?>

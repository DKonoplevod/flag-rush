angular
 .module( 'MyApp', [] )
 .service( 'NotifyService', [ '$rootScope', function( $rootScope ) {
   return {
      ai:0,
      alerts: [],
      add: function( message, type ) {
        this.alerts.push( {"id":this.ai,"message": message, "type":'alert-'+type} );
        this.ai++;
        $rootScope.$broadcast( 'NotifyService.update', this.alerts );
      },
      remove: function( id ) {
        for (var i in this.alerts)
            if (this.alerts[i].id==id) {
                this.alerts.splice(i,1);
            }
        $rootScope.$broadcast( 'NotifyService.update', this.alerts );
      }

   };
 }])
 .service( 'AppService', [ '$rootScope', '$http', function( $rootScope, $http ) {
   return {
	  user: {},
	  getCurrent: function(){
		$http.jsonp('/api/user/current?callback=callback=JSON_CALLBACK').success(function(data, status, headers, config) {
			this.user = data;
			$rootScope.$broadcast('AppService.update', this.user );
			
			duration = Date.parse(data.time)-Date.parse(data.task_started_at);
			duration = (duration - duration %1000 ) /1000;
			console.log(duration);
			console.log($scope.base_time);
			//$scope.timerTime
		});
	  },
	  
   
	  
     /* add: function( message, type ) {
        this.alerts.push( {"id":this.ai,"message": message, "type":'alert-'+type} );
        this.ai++;
        $rootScope.$broadcast( 'UserService.update', this.user );
      },*/
   };
 }]) 
 
 ;



function TaskListCtrl($scope, $timeout, $http,$location, NotifyService, AppService, $rootScope) {
	$scope.tasks = [];
	$scope.task = {};
	$scope.timer = 'off';


    $scope.$on( 'NotifyService.update', function( event, alerts ) {
        $scope.alerts = alerts;
    });

	$scope.getCurrent = function(){
		$http.jsonp('/api/user/current?callback=callback=JSON_CALLBACK').success(function(data, status, headers, config) {
		  $scope.user = data;
		  /*	duration = Date.parse(data.time)-Date.parse(data.task_started_at);
			duration = (duration - duration %1000 ) /1000;
			console.log(duration);
			console.log($scope.task.base_time);
		  */
		  
		});
	}
	
	
	$scope.getDetail = function(task) {
	   //$scope.mainImageUrl = 'hhh';
      //console.log(task);
        if (task.closed==false) {
            $location.url('/?taskId='+task.id);
        }
	}

     $scope.removeNotify = function(id) {
        NotifyService.remove(id);  
    };

	$scope.getList = function() {
		$http.jsonp('/api/task/list?callback=JSON_CALLBACK').success(function(data, status, headers, config) {
			for (var i in data){
				data[i].cost= (data[i].owner)?data[i].cost:data[i].base_cost;
			}
		  $scope.tasks = data;
		});
	}
  

  
     $scope.location = $location;

	$scope.checkTask = function(flag) {
        //$location.url('/');
		$http.jsonp('/api/task/check?callback=JSON_CALLBACK&flag='+encodeURIComponent(flag)).success(function(data, status, headers, config) {
			if (data.type=='error' || data.type=='success')
				 NotifyService.add(data.message,data.type);  
			$scope.getList();
			$scope.getTask($scope.task.id);
			$scope.getCurrent();
		});
    }

	$scope.remainTask = function(flag) {
		$http.jsonp('/api/task/remain?callback=JSON_CALLBACK&id='+flag).success(function(data, status, headers, config) {
			if (data.type=='error'){
				 NotifyService.add(data.message,data.type); 
			//if (data.type=='error') {
				$scope.getList();
				$scope.getTask($scope.task.id);
				$scope.getCurrent();
			}
		});
    }

	
	$scope.freezeTask = function(duration) {
        //$location.url('/');
		$http.jsonp('/api/task/freeze?callback=JSON_CALLBACK&duration='+duration).success(function(data, status, headers, config) {
			if (data.type=='error' || data.type=='success')
				 NotifyService.add(data.message,data.type);  
			$scope.getList();
			$scope.getTask($scope.task.id);
			$scope.getCurrent();
		});
    }
	
	$scope.costTask = function(taskid, cost) {
        //$location.url('/');
		$http.jsonp('/api/task/cost?callback=JSON_CALLBACK&cost='+cost+'&id='+taskid).success(function(data, status, headers, config) {
			if (data.type=='error' || data.type=='success')
				 NotifyService.add(data.message,data.type);  
			$scope.getList();
			$scope.getTask($scope.task.id);
			$scope.getCurrent();
		});
    }
	
	
	
 	$scope.getTask = function(taskId) {
        if(taskId) {
    		$http.jsonp('/api/task/get?callback=callback=JSON_CALLBACK&id='+taskId).success(function(data, status, headers, config) {
    			data.time = (data.best_time > 0 && data.best_time < data.base_time ? data.best_time : data.base_time);
    			console.log(data.time);
    			if (data.time < 60) {
    				data.time = data.time + ' сек.'
				}
				else {
    				data.time = ((data.time - (data.time % 60)) / 60) + ' мин. ' + (data.time % 60) + ' сек.'
				}
				console.log(data.time);
    		  	$scope.task = data;
    		});
    	$scope.timer = 'on';
    	}
	}

    $scope.openTask = function(taskId) {
        //$location.url('/');
        if(taskId)
            $http.jsonp('/api/task/open?callback=JSON_CALLBACK&id='+taskId).success(function(data, status, headers, config) {
                console.log(data);
                if (data.type=='error' || data.type=='success')
                     NotifyService.add(data.message,data.type);  
					 if (data.type=='success') {
						$scope.timer = 'on';
						$scope.getCurrent();
						//$scope.timerStart();
						$scope.getList();
						$scope.getTask($scope.task.id);
						
						$scope.task = data;
					 }
                else {
	
					
					$scope.timer = 'on';
					$scope.timerTime = data.base_time;
					//$scope.timerStart();
				}
				$scope.getList();
				$scope.getTask($scope.task.id);
				$scope.getCurrent();
            });
    }

	$scope.closeTask = function(taskId) {
		if (confirm('Вы действительно хотите прекратить решение этого задания. ВНИМАНИЕ! Ваши очки потеряются и вы больше не сможете решить этот таск.')) {
            $location.url('/');
            $http.jsonp('/api/task/close?callback=JSON_CALLBACK').success(function (data, status, headers, config) {
                if (data.type == 'error' || data.type == 'success')
                    NotifyService.add(data.message, data.type);
                $scope.getList();
                $scope.getTask($scope.task.id);
                $scope.getCurrent();
            });
        }
        else {}
    }
	


    $scope.onTimeout1 = function(){
        $scope.getList();
        $scope.getCurrent();
        $timeout($scope.onTimeout1,10000);
    }
    $timeout($scope.onTimeout1,0);
	
	/*СМ ВЫШЕ
	$scope.onTimeout = function(){
		$scope.getCurrent();
        $timeout($scope.onTimeout,10000);
    }
    $timeout($scope.onTimeout,0);
*/

/*
	$scope.onRemainTask = function(){
		if ($scope.taskId)
			$scope.remainTask($scope.taskId);
        $timeout($scope.onRemainTask,1000);
    }
    $timeout($scope.onRemainTask,0);
*/
	
    $scope.$watch('location.search()', function() {
        $scope.taskId = ($location.search()).taskId;
        $scope.getTask($scope.taskId);
    }, true);

    $scope.ooops = function(id){
    	$timeout(function(){$scope.removeNotify(id)},5000);
    }

    $scope.timerStart = function(){
		if ($scope.timer == 'on') {
			$scope.task.time_remain--;
			$scope.task.solving_time++;
			console.log($scope.task.time_remain);
			if ($scope.task.time_remain==0){
				$scope.getTask($scope.task.id);
				$scope.remainTask($scope.task.id);

			}
			$timeout($scope.timerStart, 1000);
		}
    }
	$timeout($scope.timerStart,1000);
}
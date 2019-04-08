        function getUrl(){
            let current_url = window.location.href;
            let params = current_url.split('?');
            let url =  '';
            //没有参数
            if (params.length == 1){
                url += '?'
            }
            else {
                for (i = 0; i < params.length; i++) {
                    if (params[i].indexOf('page') == -1) {
                        if (i==0){
                            url += params[i] + '?'
                        }else{
                            url += params[i] + '&'
                        }
                    }
                }
            }
            return url
        }
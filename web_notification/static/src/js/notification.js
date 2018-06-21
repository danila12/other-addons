(function() {
    openerp.web.WebClient.include({
        declare_bus_channel: function() {
            this._super();
            var self = this,
                channel = 'notify_res_user_' + this.session.uid;
            this.bus_on(channel, function(message) {
                if (message.mode == 'warn'){
                    var audio = new Audio("/web_notification/static/sound/sounds-w.mp3");
                    
                    audio.play();                	
                    self.do_warn(message.subject,
                                 message.body,
                                 message.sticky);
                }else{
                    if (message.mode == 'notify'){
                    	 
                        var audio = new Audio("/web_notification/static/sound/sounds-n.mp3");
                        
                        audio.play();
                        self.do_notify(message.subject,
                                       message.body,
                                       message.sticky);
                    }
                }
            });
            this.add_bus_channel(channel);
        },
    });
})();

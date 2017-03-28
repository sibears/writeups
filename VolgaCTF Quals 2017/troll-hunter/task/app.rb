require 'sinatra'
require 'open-uri'
require 'openssl'
require 'elastics'
require 'uri'

set :port, 9494
set :show_exceptions, false


get('/show') do 
    begin
    id = params[:id]
    print id
    print  URI.escape(id)
    id = URI.escape(id)
    client = Elastics::Client.new({:host => '127.0.0.1:9200',  :index => 'information',  :type => 'troll'})    
    data = client.request({:id=>"_search?#{id}"})
    data['hits']['hits'][0]['_source']
    data = data['hits']['hits'][0]['_source']
    
    if not defined?(data['name']) then
        data = "Problem with Connection";
    end
    print data
    rescue
    data = "Problem with Connection";
    end
    if (data === "Problem with Connection") then
        erb :error , :locals => { :data => data}  
    else erb :page, :locals => { :data => data} end
    # if not data['_source'] then erb :error, :locals => { :data => 'Can not fetch from database'} end
    

    
end
post('/checkip') do
    # ip = params [:ip]
    begin
    	OpenSSL::SSL::VERIFY_PEER = OpenSSL::SSL::VERIFY_NONE
    	ip = params[:ip]
        url = 'http://'+URI(ip).host+':'+(URI(ip).port).to_s
    	data = URI.parse(url).read
        res = "Ok. We'll check this. Thank you!"
    rescue
    	res = "Sorry, we can't check this ip. Something wrong"
    end


    res
    # erb :list, :locals => {:ip => params[:ip], :data => res}
end
get('/*') do
begin
client = Elastics::Client.new({:host => '127.0.0.1:9200',  :index => 'information',  :type => 'troll'})
res = client.request({:id=>'_search?q=*'})
rescue
res = "Problem with Connection";
end
erb :list, :locals => { :data => res['hits']['hits']}
end






not_found do
     status 404
     "Something wrong! Try to type URL correctly or call to UFO."
end
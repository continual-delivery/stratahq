local _M = {}

-- Initialize a cache on the module level with up to 1000 entries
local lrucache = require("resty.lrucache")
local c, err = lrucache.new(1000)
if not c then
    return error("failed to create the cache: " .. (err or "unknown"))
end

function _M.go()
    --  fetch values from request
    local check_host = ngx.var.check_host
    local check_port = ngx.var.check_port
    local ckey = check_host .. "_" .. check_port

    -- Check the cache for a value
    local data, stale_data = c:get(ckey)
    if not data then

        -- Create a socket and test connection
        local sock = ngx.socket.tcp()
        sock:settimeout(1000)

        local ok, err = sock:connect(check_host, check_port)
        if not ok then
            ngx.status = ngx.HTTP_BAD_GATEWAY
            ngx.say("fail: ", err)
            c:delete(ckey)
            return
        end
        sock:close()

        -- Put result in cache with a TTL of 5 seconds
        c:set(ckey, "ok", 5)
    end

    -- Port is listening
    ngx.status = ngx.HTTP_OK
    ngx.say(c:get(ckey))
end

return _M
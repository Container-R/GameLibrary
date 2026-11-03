-- Original finite Lua 5.4 fixture. Prepared, not executed.
assert(_VERSION == 'Lua 5.4', 'unexpected Lua series')
local function check(v) assert(v, 'fixture assertion failed') end
local function branch(mode)
    local events, closes, close_error = {}, 0, nil
    local sentinel = {} -- identity only, never printed or converted to text
    local co = coroutine.create(function()
        local resource <close> = setmetatable({}, {__close = function(_, err)
            closes = closes + 1
            close_error = err
            events[#events + 1] = 'close'
        end})
        events[#events + 1] = 'enter'
        coroutine.yield('waiting')
        if mode == 'error' then
            events[#events + 1] = 'before-error'
            error(sentinel, 0)
        end
        events[#events + 1] = 'after-yield'
        return 'done'
    end)
    local first = table.pack(coroutine.resume(co))
    check(first.n == 2 and first[1] == true and first[2] == 'waiting')
    check(coroutine.status(co) == 'suspended' and closes == 0)
    check(table.concat(events, ',') == 'enter')
    print(mode .. '|yield|n=2|ok=true|value=waiting|state=suspended|closes=0|events=enter')
    if mode == 'normal' then
        local result = table.pack(coroutine.resume(co))
        check(result.n == 2 and result[1] == true and result[2] == 'done')
        check(coroutine.status(co) == 'dead' and closes == 1 and close_error == nil)
        check(table.concat(events, ',') == 'enter,after-yield,close')
        print('normal|finish|n=2|ok=true|value=done|state=dead|closes=1|close_error_nil=true|events=enter,after-yield,close')
    elseif mode == 'close' then
        local result = table.pack(coroutine.close(co))
        check(result.n == 1 and result[1] == true)
        check(coroutine.status(co) == 'dead' and closes == 1 and close_error == nil)
        check(table.concat(events, ',') == 'enter,close')
        print('close|finish|n=1|ok=true|state=dead|closes=1|close_error_nil=true|events=enter,close')
    else
        local failed = table.pack(coroutine.resume(co))
        check(failed.n == 2 and failed[1] == false and rawequal(failed[2], sentinel))
        check(coroutine.status(co) == 'dead' and closes == 0)
        check(table.concat(events, ',') == 'enter,before-error')
        print('error|resume-error|n=2|ok=false|error_identity=true|state=dead|closes=0|events=enter,before-error')
        local result = table.pack(coroutine.close(co))
        check(result.n == 2 and result[1] == false and rawequal(result[2], sentinel))
        check(coroutine.status(co) == 'dead' and closes == 1 and rawequal(close_error, sentinel))
        check(table.concat(events, ',') == 'enter,before-error,close')
        print('error|finish|n=2|ok=false|error_identity=true|state=dead|closes=1|close_error_identity=true|events=enter,before-error,close')
    end
end
branch('normal')
branch('close')
branch('error')

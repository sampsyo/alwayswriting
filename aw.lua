#!/usr/bin/env lua
require "wsapi.request"
require "wsapi.response"
require "wsapi.fastcgi"
require "lsqlite3"

-- Initialize randomness, as suggested by:
-- http://lua-users.org/wiki/MathLibraryTutorial
-- Maybe replace with lrandom if this seems to predictable.
math.randomseed(os.time())
math.random() ; math.random() ; math.random() ; math.random()

TEMPLATE_NAME = 'aw.html'
TEMPLATE_SUB = 'WORDS!'
COUNT = 5

local db = sqlite3.open('words.db')

local nwords
for row in db:rows("select count() from 'words'") do
    nwords = row[1]
    break
end

local template = assert(io.open(TEMPLATE_NAME)):read('*all')

local function getaword()
    local index = math.random(nwords)
    for row in db:rows("select word from 'words' where id="..index) do
        return row[1]
    end
end

local function genpage()
    local lst = ''
    for i = 1, COUNT do
        lst = lst .. '<li>' .. getaword() .. '</li>\n'
    end
    local out = template:gsub(TEMPLATE_SUB, lst)
    return out
end

-- print(genpage())

local function handler(env)
    local request = wsapi.request.new(env)
    local response = wsapi.response.new()
    
    response['Content-Type'] = 'text/html'
    response:write(genpage())
    
    return response:finish()
end

wsapi.fastcgi.run(handler)

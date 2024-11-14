local quotedfilepath = '"' .. filepath .. '"'

local command = "mscore -a jack -o /tmp/output.pdf  " ..quotedfilepath

-- Open the file "mscore.sh" for writing
local file = io.open("mscore.sh", "w")



if not file then
    -- Handle error if file couldn't be opened
    print("Error: Failed to create file 'mscore.sh'")
else
    -- Write the command content to the file


    file:write(command .. "\n") -- Write the command to the file

    -- Close the file
    file:close()

    print("File 'mscore.sh' created successfully!")

    -- Delete the file after printing the success message

end

local mv = "mv mscore.sh /tmp/mscore.sh"

os.execute(mv)

os.forkexec("/bin/bash", "/tmp/mscore.sh")

current_fileset -simset [get_filesets sim_1]
for {set i 0} {$i < 500} {incr i} {
    set_property top test_$i [get_filesets sim_1]
    set_property top_lib xil_defaultlib [get_filesets sim_1]
    launch_simulation -mode behavioral
    run 10 us
    close_sim
    launch_simulation -mode post-synthesis -type functional
    run 10 us
    close_sim
    launch_simulation -mode post-synthesis -type timing
    run 10 us
    close_sim  
} 

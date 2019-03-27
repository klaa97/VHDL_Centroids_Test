from random import randint
from random import choice
from random import shuffle
from enum import Enum

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def taxicab_distance(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

def near_point(p, distance):
    offset_x = randint(0,distance)
    offset_y = distance - offset_x
    x = p.x + choice([offset_x,-offset_x])
    y = p.y + choice([offset_y,-offset_y])
    return Point(x,y)    

def gen_test(n_mask_1, min_same_distance, distance):
    masks = [str.zfill(bin(i)[2:],8) for i in range(256)]
    mask_in = choice([i for i in masks if i.count('1') == n_mask_1])
    p = Point(randint(distance,255 - distance),randint(distance,255 - distance))
    centroids = [None] * 8
    positions = [i for i in range(8)]
    shuffle(positions)
    for i in positions:
        if mask_in[i] == '1' and min_same_distance > 0:
            centroids[i] = near_point(p, distance)
            min_same_distance -= 1
        else:
            c = Point(randint(0,255),randint(0,255))
            while taxicab_distance(c,p) < distance:
                c = Point(randint(0,255),randint(0,255))         
            centroids[i] = c
    distances = [taxicab_distance(centroids[i], p) for i in range(8)]
    mask_out = ''.join('1' if (distances[i] <= min(distances) and mask_in[i] == '1') else '0' for i in range(8))
    return mask_in,mask_out,p,centroids

def create_seq_tbenchs(list_n_mask_1, list_min_same_distance, list_distance, n_tests, filename):
    options = [gen_test(list_n_mask_1[i], list_min_same_distance[i], list_distance[i]) for i in range(n_tests)]
    test = """library ieee;
                use ieee.std_logic_1164.all;
                use ieee.numeric_std.all;
                use ieee.std_logic_unsigned.all;
                entity {0} is
                end {0};
                architecture projecttb of {0} is
                constant c_CLOCK_PERIOD		: time := 100 ns;
                signal   tb_done		: std_logic;
                signal   mem_address		: std_logic_vector (15 downto 0) := (others => '0');
                signal   tb_rst	                : std_logic := '0';
                signal   tb_start		: std_logic := '0';
                signal   tb_clk		        : std_logic := '0';
                signal   mem_o_data,mem_i_data	: std_logic_vector (7 downto 0);
                signal   enable_wire  		: std_logic;
                signal   mem_we		        : std_logic;
                type ram_type is array (65535 downto 0) of std_logic_vector(7 downto 0);
                signal RAM: ram_type := (""".format(filename.split('.')[0])
    test += '0 => "{}",\n'.format(options[0][0])
    for i in range (8):
        test += "{} => std_logic_vector(to_unsigned( {}, 8)),\n".format(i*2+1,options[0][3][7-i].x)
        test += "{} => std_logic_vector(to_unsigned( {}, 8)),\n".format(i*2+2,options[0][3][7-i].y)
    test += "17 => std_logic_vector(to_unsigned( {}, 8)),\n".format(options[0][2].x)
    test += "18 => std_logic_vector(to_unsigned( {}, 8)),\n others => (others => '0'));\nsignal count : integer := 0;\n".format(options[0][2].y)
    test += "-- MASK_OUT: \t {}\n".format(options[0][1])
    test += """ component project_reti_logiche is
                port (
                    i_clk         : in  std_logic;
                    i_start       : in  std_logic;
                    i_rst         : in  std_logic;
                    i_data        : in  std_logic_vector(7 downto 0);
                    o_address     : out std_logic_vector(15 downto 0);
                    o_done        : out std_logic;
                    o_en          : out std_logic;
                    o_we          : out std_logic;
                    o_data        : out std_logic_vector (7 downto 0)
                    );
                end component project_reti_logiche;
                begin
                UUT: project_reti_logiche
                port map (
                        i_clk      	=> tb_clk,
                        i_start       => tb_start,
                        i_rst      	=> tb_rst,
                        i_data    	=> mem_o_data,
                        o_address  	=> mem_address,
                        o_done      	=> tb_done,
                        o_en   	=> enable_wire,
                        o_we 		=> mem_we,
                        o_data    	=> mem_i_data
                        );
                p_CLK_GEN : process is
                begin
                    wait for c_CLOCK_PERIOD/2;
                    tb_clk <= not tb_clk;
                end process p_CLK_GEN;
                MEM : process(tb_clk)
                begin
                    if tb_clk'event and tb_clk = '1' then
                        if enable_wire = '1' then
                            if mem_we = '1' then
                                RAM(conv_integer(mem_address))  <= mem_i_data;
                                mem_o_data                      <= mem_i_data after 2 ns;
                            else
                                mem_o_data <= RAM(conv_integer(mem_address)) after 2 ns;
                            end if;
                        end if;
                    else """
    for j in range(1,n_tests):
        if (j!=1):
            test += """els"""
        test += """if count = {} then RAM <= (""".format(j)
        test += '0 => "{}",\n'.format(options[j][0])
        for i in range (8):
            test += "{} => std_logic_vector(to_unsigned( {}, 8)),\n".format(i*2+1,options[j][3][7-i].x)
            test += "{} => std_logic_vector(to_unsigned( {}, 8)),\n".format(i*2+2,options[j][3][7-i].y)
        test += "17 => std_logic_vector(to_unsigned( {}, 8)),\n".format(options[j][2].x)
        test += "18 => std_logic_vector(to_unsigned( {}, 8)),\n others => (others => '0'));\n".format(options[j][2].y)
        test += "-- MASK_OUT: \t {}\n".format(options[j][1])
    test += """end if; end if;
                end process;
                test : process is
                begin """
    test += """ wait for 100 ns;
                    wait for c_CLOCK_PERIOD;
                    tb_rst <= '1';
                    wait for c_CLOCK_PERIOD;
                    tb_rst <= '0'; """
    for j in range(n_tests):
        test +="""  wait for c_CLOCK_PERIOD;
                    count <= {};
                    wait for c_CLOCK_PERIOD;
                    count <= 0;
                    tb_start <= '1';
                    wait for c_CLOCK_PERIOD;
                    wait until tb_done = '1';
                    wait for c_CLOCK_PERIOD;
                    tb_start <= '0';
                    wait until tb_done = '0';
                    assert RAM(19) = "{}" report "TEST FAILED" severity failure;""".format(j,options[j][1])
    test += """\nassert false report "{} TESTS PASSED" severity failure;
    end process test;
                end projecttb;""".format(n_tests)
    with open(filename, "w") as f:
        f.write(test)
    

def create_tbench(n_mask_1, min_same_distance, distance,filename):
    mask_in,mask_out,p,centroids = gen_test(n_mask_1, min_same_distance, distance)
    test = "-- MASK_IN:\t{}\n-- MASK_OUT:\t{}\n".format(mask_in,mask_out)
    test += "-- Point =\t({},{})\n".format(p.x,p.y)
    for i in range(0,8):
        test+= "-- Centroid {} =\t({},{})\n".format(i+1,centroids[i].x,centroids[i].y)
    test += """library ieee;
                use ieee.std_logic_1164.all;
                use ieee.numeric_std.all;
                use ieee.std_logic_unsigned.all;
                entity {0} is
                end {0};
                architecture projecttb of {0} is
                constant c_CLOCK_PERIOD		: time := 100 ns;
                signal   tb_done		: std_logic;
                signal   mem_address		: std_logic_vector (15 downto 0) := (others => '0');
                signal   tb_rst	                : std_logic := '0';
                signal   tb_start		: std_logic := '0';
                signal   tb_clk		        : std_logic := '0';
                signal   mem_o_data,mem_i_data	: std_logic_vector (7 downto 0);
                signal   enable_wire  		: std_logic;
                signal   mem_we		        : std_logic;
                type ram_type is array (65535 downto 0) of std_logic_vector(7 downto 0);
                signal RAM: ram_type := (""".format(filename.split('.')[0])
    test += '0 => "{}",\n'.format(mask_in)
    for i in range (8):
        test += "{} => std_logic_vector(to_unsigned( {}, 8)),\n".format(i*2+1,centroids[7-i].x)
        test += "{} => std_logic_vector(to_unsigned( {}, 8)),\n".format(i*2+2,centroids[7-i].y)
    test += "17 => std_logic_vector(to_unsigned( {}, 8)),\n".format(p.x)
    test += "18 => std_logic_vector(to_unsigned( {}, 8)),\n others => (others => '0'));\n".format(p.y)
    test += """ component project_reti_logiche is
                port (
                    i_clk         : in  std_logic;
                    i_start       : in  std_logic;
                    i_rst         : in  std_logic;
                    i_data        : in  std_logic_vector(7 downto 0);
                    o_address     : out std_logic_vector(15 downto 0);
                    o_done        : out std_logic;
                    o_en          : out std_logic;
                    o_we          : out std_logic;
                    o_data        : out std_logic_vector (7 downto 0)
                    );
                end component project_reti_logiche;
                begin
                UUT: project_reti_logiche
                port map (
                        i_clk      	=> tb_clk,
                        i_start       => tb_start,
                        i_rst      	=> tb_rst,
                        i_data    	=> mem_o_data,
                        o_address  	=> mem_address,
                        o_done      	=> tb_done,
                        o_en   	=> enable_wire,
                        o_we 		=> mem_we,
                        o_data    	=> mem_i_data
                        );
                p_CLK_GEN : process is
                begin
                    wait for c_CLOCK_PERIOD/2;
                    tb_clk <= not tb_clk;
                end process p_CLK_GEN;
                MEM : process(tb_clk)
                begin
                    if tb_clk'event and tb_clk = '1' then
                        if enable_wire = '1' then
                            if mem_we = '1' then
                                RAM(conv_integer(mem_address))  <= mem_i_data;
                                mem_o_data                      <= mem_i_data after 2 ns;
                            else
                                mem_o_data <= RAM(conv_integer(mem_address)) after 2 ns;
                            end if;
                        end if;
                    end if;
                end process;
                test : process is
                begin 
                    wait for 100 ns;
                    wait for c_CLOCK_PERIOD;
                    tb_rst <= '1';
                    wait for c_CLOCK_PERIOD;
                    tb_rst <= '0';
                    wait for c_CLOCK_PERIOD;
                    tb_start <= '1';
                    wait for c_CLOCK_PERIOD;
                    wait until tb_done = '1';
                    wait for c_CLOCK_PERIOD;
                    tb_start <= '0';
                    wait until tb_done = '0';
                    assert RAM(19) = "{}" report "TEST FAILED" severity failure;\n
                    assert false report "TEST PASSED" severity failure;
                end process test;
                end projecttb;""".format(mask_out)
    with open(filename, "w") as f:
        f.write(test)
if __name__ == "__main__":
    n_test =1000
    create_seq_tbenchs([randint(6,7) for i in range(n_test)],[randint(4,6) for i in range(n_test)],[randint(30,80) for i in range(n_test)],n_test,"multiple_test.vhd")

        
    



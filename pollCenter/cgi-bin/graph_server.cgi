#!/usr/bin/perl -wT

use strict;
use DBI;
use lib '/home/abrooks/www/pollCenter/script_src';
use DbConfig;
use CGI qw /:standard/;
use CGI::Carp;
use Util;
use Data::Dumper;

my $JSON;
my $q = new CGI;
my $initSessionObject = Util::validateSession('pollCenterID','qID');

if (ref $initSessionObject eq 'SessionObject') 
{
    
   my $pollIDparm = $q->param('poll_ids');
   carp("############ $pollIDparm ###################");

   if (defined($pollIDparm))
   {
    
       my $dbconf = DbConfig->new();
    
       my $dbh = DBI->connect( "dbi:mysql:"
                        . $dbconf->dbName() . ":"
                        . $dbconf->dbHost(),
                        $dbconf->dbUser(),
                        $dbconf->dbPass(), $::attr )
                        or die "Cannot Connect to Database $DBI::errstr\n";
    
       
       $JSON = " [ ";

       my @a = ();
       for my $pollID (split(":", $pollIDparm))
       {
        
           carp("########## pollID - $pollID - pollID ##############");
           my @row_array  = $dbh->selectrow_array("select * from poll where poll_id = $pollID");
           ## add exception logic#
           #######################

           my $pollObj = genJSON(\@row_array);
	   #$JSON .= $pollObj . ", ";
	  $a[++$#a] = $pollObj;
       }
      
       $JSON .= $a[0] . " ";;  

       for(my $i=1; $i < scalar(@a); $i++)
       {
	   $JSON .= "," . $a[$i]; 
       }
       
      $JSON .= " ]  ";

   }         

   print $q->header( -status=> '200 OK',
		-Content_Type=>'application/json');

   print $JSON;

   carp("######## JSON OUT ################");
   print STDERR $JSON;
   carp("######## JSON OUT ################");

}


sub genJSON
{

   ##  JSON parsing of property - renderer:$.jqplot.BarRenderer not handled well client side even with escapes
   ##  will reset explicit on client side.
   my @row_data = @{(shift)};
   my ($poll_id,$poll_desc,$poll_optionslist,$poll_optlistflag,$category_id,$creation_ts) = (0..4,25); 

   my $jsJQPlotBarColors = " \"seriesColors\" : [ \"blue\", \"#c5b47f\", \"#EAA228\", \"#579575\", \"#839557\" ]";

   my $jsJQPlotSeriesDefs = "  \"seriesDefaults\" : { 					 \	
                                                   \"renderer\" : \"\$.jqplot.BarRenderer\",	 \	
                                         	   \"markerOptions\" : { },\
                                                   \"rendererOptions\" : { \"barWidth\" : null } 	\	
                                               }";

   my $jsJQPlotAxes = " \"axes\" : { 					\
                  	             \"xaxis\" : {				\
                                         \"tickOptions\" : { \"show\": false },	\
                                         \"showTicks\" : false,		\
                                         \"showTickMarks\" : false		\
                                        },				\
				     \"yaxis\" : { 		\
                                         \"tickOptions\" : { },	\
					  \"min\": 0, \
					  \"numberTicks\": 5\
				      } \
                         }";

   my $jsJQPlotLegend = "  \"legend\" : {			\
                                       \"show\" : true,	\
                                       \"location\" : \"e\",	\
                                       \"yoffset\" : 15,	\
                                       \"xoffset\" : 15	\
                                   }";


   ### for getting names and values of poll options
   my $colShiftNames = 5; 
   my $colShiftVals = 15; 

   my %pollDataHash = ();

   for(my $i=0; $i < 10; $i++)
   {
       if(defined($row_data[$colShiftNames + $i]))	  
       {
           $pollDataHash{$row_data[$colShiftNames + $i]} = $row_data[$colShiftVals + $i]; 
       } 
       else
       {
	   last;
       }

   }

   ### JS overrides gen for JqPlot ###
   my @pollOption = (sort keys %pollDataHash); 

   my $seriesOverRides = " \"series\" : [ ";

   $seriesOverRides .= " { \"label\" : \"" . $pollOption[0] . "\" } ";

   for (my $i=1; $i < scalar(@pollOption); $i++)
   {
       $seriesOverRides .= ", { \"label\" : \"" . $pollOption[$i] . "\" } ";
   }

   $seriesOverRides .= " ]";

   ### JS data array gen for JqPlot ### 
   my $seriesData = " [";

   my @pollKeyData = (sort keys %pollDataHash);

   $seriesData .= " [" . $pollDataHash{$pollKeyData[0]} . "] "; 

   for(my $i=1; $i < scalar(@pollKeyData); $i++)
   {
       $seriesData .= ", [" . $pollDataHash{$pollKeyData[$i]} . "] ";
   } 

   $seriesData .= " ] ";

   my $optionsObj = sprintf("{%s,\n%s,\n%s,\n%s,\n%s\n}",
			$jsJQPlotBarColors,$jsJQPlotSeriesDefs,$jsJQPlotLegend,
							$jsJQPlotAxes,$seriesOverRides);

   my $pollObj = sprintf("{\n \"data\" :%s,\n \"options\" :\n\t%s\n}\n",$seriesData,$optionsObj);    

   return $pollObj;

}

sub genJSON2
{
   my @row_data = @{(shift)};
   my ($poll_id,$poll_desc,$poll_optionslist,$poll_optlistflag,$category_id,$creation_ts) = (0..4,25); 

   my $jsJQPlotBarColors = " seriesColors: [ 'blue', '#c5b47f', '#EAA228', '#579575', '#839557' ]";

   my $jsJQPlotSeriesDefs = "  seriesDefaults: { 					 \	
                                                   renderer: \$.jqplot.BarRenderer,	 \	
                                                   rendererOptions: { barWidth : null } 	\	
                                               }";

   my $jsJQPlotAxes = " axes: { 					\
                  	             xaxis: {				\
                                         tickOptions: { show: false },	\
                                         showTicks: false,		\
                                         showTickMarks: false		\
                                        }				\
                             } ";

   my $jsJQPlotLegend = "  legend: {			\
                                       show: true,	\
                                       location: 'e',	\
                                       yoffset: 15,	\
                                       xoffset: 15	\
                                   } ";


   ### for getting names and values of poll options
   my $colShiftNames = 5; 
   my $colShiftVals = 15; 

   my %pollDataHash = ();

   for(my $i=0; $i < 10; $i++)
   {
       if(defined($row_data[$colShiftNames + $i]))	  
       {
           $pollDataHash{$row_data[$colShiftNames + $i]} = $row_data[$colShiftVals + $i]; 
       } 
       else
       {
	   last;
       }

   }

   ### JS overrides gen for JqPlot ###
   my @pollOption = (sort keys %pollDataHash); 

   my $seriesOverRides = " series: [ ";

   $seriesOverRides .= " { label: '" . $pollOption[0] . "' } ";

   for (my $i=1; $i < scalar(@pollOption); $i++)
   {
       $seriesOverRides .= ", { label: '" . $pollOption[$i] . "' } ";
   }

   $seriesOverRides .= " ]";

   ### JS data array gen for JqPlot ### 
   my $seriesData = " [";

   my @pollKeyData = (sort keys %pollDataHash);

   $seriesData .= " [" . $pollDataHash{$pollKeyData[0]} . "] "; 

   for(my $i=1; $i < scalar(@pollKeyData); $i++)
   {
       $seriesData .= ", [" . $pollDataHash{$pollKeyData[$i]} . "] ";
   } 

   $seriesData .= " ] ";

   my $optionsObj = sprintf("{%s,\n%s,\n%s,\n%s,\n%s\n}",
			$jsJQPlotBarColors,$jsJQPlotSeriesDefs,$jsJQPlotLegend,
							$jsJQPlotAxes,$seriesOverRides);

   my $pollObj = sprintf("{\n data: %s,\n options: %s\n}\n",$seriesData,$optionsObj);    

   return $pollObj;

}

exit;

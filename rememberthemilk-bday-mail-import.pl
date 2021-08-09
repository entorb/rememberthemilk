#!/bin/perl -w
# reads a vcf addressbook file
# skips all but whitelisted one-line files of that file
# skips all cards not containing a birthday
# generates a list of upcoming birthdays
# send this list via email to my remember the milk account

# Modules: My Default Set
use strict;
use warnings;

use 5.010;
use utf8;       # this script is written in UTF-8
use autodie;    # Replace functions with ones that succeed or die with lexical scope
# use Data::Dumper;

# Modules: Perl Standard
use Time::Local;

# Encoding
use Encode qw(encode decode);
# use open ':encoding(UTF-8)';    # default encoding for all files, not working for open( my $fhIn, '<', $fileIn )
# default encoding for print STDOUT
if ( $^O eq 'MSWin32' ) {
  binmode( STDOUT, ':encoding(cp850)' );
} else {
  binmode( STDOUT, ':encoding(UTF-8)' );
}

# Modules: File Access
use File::Basename;

# Start
our $VERSION = '2020-01-24';

# TODO: enter your data
my $fileIn                  = 'addressbook.vcf';
my $email_taskTags          = '#myList #MyTag';
my $email_taskImportAddress = 'myImportAddress@rmilk.com';

my $export_bday_vcf = 0;    # set to 1 if you want an exported copy

# chdir to dir of perl file
chdir dirname( __FILE__ );

# whiteliste of fields to keep
my $fieldsAllowed = join '|', qw ( BEGIN END BDAY N );

my @cont;
open( my $fhIn, '<:encoding(UTF-8)', $fileIn ) or die $!;
# whilelist of only lines that start with one of the allowed keywords. (these must be single-line-keywords)
# @cont = grep {m/^($fieldsAllowed)[:;].*/} <$fhIn>;
while ( my $line = <$fhIn> ) {
  next if not $line =~ m/^($fieldsAllowed)[:;].*/;
  $line =~ s/\r\n$/\n/;    #Linebreaks; Windows -> Linux
  push @cont, $line;
}
# say $#cont;
close $fhIn;

# filter to only cards having bdays
my @cards = split m/BEGIN:VCARD/, join( '', @cont );
undef @cont;
@cards = grep {m/\nBDAY[;:]/} @cards;

if ( $export_bday_vcf != 0 and $#cards > 0 ) {
  # export addressbook of only birthdays
  my ( $fname, $fdir, $fext ) = fileparse( $fileIn, qr/[.][^.]*/ );
  my $fileOut = "$fname-BdayOnly$fext";
  open( my $fhout, '>', $fileOut ) or die $!;
  print { $fhout } 'BEGIN:VCARD' . join 'BEGIN:VCARD', @cards;
  close $fhout;
} ## end if ( $export_bday_vcf ...)

#
#
# generate at print bday list
#
#

# my $offsetDaysPast   = 70; # this is a bit more difficult to handly
my $offsetDaysFuture = 14;

@_ = localtime( time );
my ( $today_day, $today_mon, $today_year ) = ( $_[ 3 ], $_[ 4 ] + 1, $_[ 5 ] + 1900 );
my $today_ts = timelocal( 0, 0, 0, $today_day, $today_mon - 1, $today_year );

# @_ = localtime( time - 24 * 3600 * $offsetDaysPast );
# my ( $start_day, $start_mon, $start_year ) = ( $_[ 3 ], $_[ 4 ] + 1, $_[ 5 ] + 1900 );


sub calcdays {
  my ( $y1, $m1, $d1, $y2, $m2, $d2 ) = @_;
  # calculates date2-date1 in days
  # argument = y1,m1,d1,y2,m2,d2
  my $time1 = timelocal( 0, 0, 0, $d1, $m1 - 1, $y1 );
  my $time2 = timelocal( 0, 0, 0, $d2, $m2 - 1, $y2 );
  return int( ( $time2 - $time1 ) / 3600 / 24 );
} ## end sub calcdays


sub calcdaysFromToday {
  my ( $y1, $m1, $d1 ) = @_;
  # calculates date2-date1 in days
  # argument = y1,m1,d1
  my $time1 = timelocal( 0, 0, 0, $d1, $m1 - 1, $y1 );
  return int( ( $time1 - $today_ts ) / 3600 / 24 );
} ## end sub calcdaysFromToday


sub calcage {
  my ( $y, $m, $d ) = @_;
  # calcuates age
  # argument: y,m,d
  #   $d += 0;
  #   $m -= 1;
  #   $y -= 1900;
  my $time1 = timelocal( 0, 0, 0, $d, $m - 1, $y );
  return int( ( $today_ts - $time1 ) / 3600 / 24 / 365 );
} ## end sub calcage

# BEGIN:VCARD
# BDAY:19700102
# N:Meier;Hans;;;
# END:VCARD

my @bdaycalender;
$_ = sprintf '%04d-%02d-%02d => generation <=', $today_year, $today_mon, $today_day;    # marker for today
push @bdaycalender, $_;

foreach my $card ( @cards ) {
  my @bday;
  if ( $card =~ m/\nBDAY[^:]*:(\d{4})(\d{2})(\d{2})\n/ ) {                                   # 19700102
    @bday = ( $1, $2, $3 );
  } elsif ( $card =~ m/\nBDAY[^:]*:(\d{4})\-(\d{2})\-(\d{2})/ ) {                            # 1970-01-02
    @bday = ( $1, $2, $3 );
  } else {
    die "E: no bday in $card";
  }
  $card =~ m/\nN:([^;]+);([^;]+)/;
  my $name = "$2 $1";
  # say "$bday[0]-$bday[1]-$bday[0] - $name";

  # find year of next bday
  # check if birtday has already been this year, if so it it next year
  my $yearNextBday = $today_year;
  my $daysDiff     = calcdaysFromToday( $today_year, $bday[ 1 ], $bday[ 2 ] );
  $yearNextBday++ if ( $daysDiff < 0 );

  # how many days till next birthday?
  my $daysTillNextBday = calcdaysFromToday( $yearNextBday, $bday[ 1 ], $bday[ 2 ] );

  # store in array if in the desired future via parameter offsetDaysFuture
  if ( $daysTillNextBday <= $offsetDaysFuture ) {    # $daysTillNextBday >= -$offsetDaysPast and
    my $age = calcage( $bday[ 0 ], $bday[ 1 ], $bday[ 2 ] );
    $_ = "$yearNextBday-$bday[1]-$bday[2] $name ($age)";
    push @bdaycalender, $_;
  }
} ## end foreach my $card ( @cards )

# sort the generated list (by bday)
@bdaycalender = sort { $a cmp $b } @bdaycalender;

# on windows: print
if ( $^O eq 'MSWin32' ) {
  foreach my $line ( @bdaycalender ) {
    say $line;
  }
}


sub send_mail {
  # in: $subject, $body, $to_address
  # out: nothing
  # send an email
  my ( $subject, $body, $to_address ) = @_;
  $subject = encode( 'UTF-8', $subject );
  $body    = encode( 'UTF-8', $body );
  my $mailprog = '/usr/lib/sendmail';
  insertNewEMail($to_address, $subject, $body);
  # open( my $fh, "| $mailprog -t" ) || print { *STDERR } "Mail-Error\n";
  # print { $fh } "To: $to_address\n";
  # print { $fh } "Subject: $subject\n";
  # print { $fh } "Content-Type: text/plain; charset=\"utf-8\"\n";
  # print { $fh } "\n$body";                                         # \n starts body
  # close $fh;
  return;
} ## end sub send_mail


sub insertNewEMail {
  my ( $send_to, $subject, $body, $send_from ) = @_;    # , $send_cc, $send_bcc

  use lib ( '/var/www/virtual/entorb/perl5/lib/perl5' );
  my $PATH = "/var/www/virtual/entorb/mail-daemon/outbox.db";
  use DBI;
  my $dbh = DBI->connect( "dbi:SQLite:dbname=$PATH", "", "" );
  $dbh->{ AutoCommit } = 0;

  my $sth = $dbh->prepare( "INSERT INTO outbox(send_to, subject, body, send_from, send_cc, send_bcc, date_created, date_sent) VALUES (?, ?, ?, ?, '', '', CURRENT_TIMESTAMP, NULL)" );
  $sth->bind_param( 1, $send_to,   DBI::SQL_VARCHAR );
  $sth->bind_param( 2, $subject,   DBI::SQL_VARCHAR );
  $sth->bind_param( 3, $body,      DBI::SQL_VARCHAR );
  $sth->bind_param( 4, $send_from, DBI::SQL_VARCHAR );
  $sth->execute;
  $dbh->commit;
} ## end sub insertNewEMail

my $subject = "BDay $email_taskTags =15min ~today ^1 week !3";
my $body    = '';
foreach my $line ( @bdaycalender ) {
  # say $line;
  $body .= "$line\n";
}

# on linux server : send mail
if ( $^O ne 'MSWin32' ) {
  # say "sende Mail: SUB: $subject\nBODY: $body\nTO:$email_taskImportAddress";
  send_mail( $subject, $body, $email_taskImportAddress );
}

1;

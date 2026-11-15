rule lab_lexcorp {
  meta:
    author = "Maxime Leal — KryptoniteSuite"
    description = "traces de kit lab"
  strings:
    $s0 = "lex_ransom2" ascii nocase
    $s1 = "lex_smb_worm" ascii nocase
    $s2 = ".lexcor" ascii nocase
  condition:
    any of them
}

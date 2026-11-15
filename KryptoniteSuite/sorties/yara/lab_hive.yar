rule lab_hive {
  meta:
    author = "Maxime Leal — KryptoniteSuite"
    description = "traces de kit lab"
  strings:
    $s0 = "ruche_worker" ascii nocase
    $s1 = "hivesync" ascii nocase
  condition:
    any of them
}

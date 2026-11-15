rule lab_star {
  meta:
    author = "Maxime Leal — KryptoniteSuite"
    description = "traces de kit lab"
  strings:
    $s0 = "star_dns_c2" ascii nocase
    $s1 = "star_c2_server" ascii nocase
  condition:
    any of them
}

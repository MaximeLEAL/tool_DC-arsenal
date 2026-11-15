rule lab_rickportal {
  meta:
    author = "Maxime Leal — KryptoniteSuite"
    description = "traces de kit lab"
  strings:
    $s0 = "RickCache" ascii nocase
    $s1 = "portal.command" ascii nocase
    $s2 = "rick_key.bin" ascii nocase
  condition:
    any of them
}

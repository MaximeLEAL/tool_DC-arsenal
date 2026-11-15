rule lab_arkham {
  meta:
    author = "Maxime Leal — KryptoniteSuite"
    description = "traces de kit lab"
  strings:
    $s0 = "ArkhamUpdate" ascii nocase
    $s1 = "lexagent" ascii nocase
    $s2 = "ArkhamAgentSingle" ascii nocase
  condition:
    any of them
}

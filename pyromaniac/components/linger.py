user = args[0]

BASE = Path('/var/lib/systemd/linger' )

{
    'storage': {
        'directories': [{ 'path': BASE }],
        'files': [{ 'path': BASE / user }],
    },
}
